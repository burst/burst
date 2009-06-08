import sys
import linecache

from burst_util import (traceme, nicefloat,
    BurstDeferred, Deferred, chainDeferreds)
from burst.events import *
import burst
import burst_consts as consts
from burst_consts import (FOV_X, FOV_Y, EVENT_MANAGER_DT,
    DEFAULT_CENTERING_X_ERROR,
    DEFAULT_CENTERING_Y_ERROR, PIX_TO_RAD_X, PIX_TO_RAD_Y,
    IMAGE_CENTER_X, IMAGE_CENTER_Y)
from burst.image import normalized2_image_width, normalized2_image_height
from math import pi

# This is used for stuff like Localization, where there is an error
# that is reduced by having a smaller error - otoh tracker will take longer
# (possibly)
TRACKER_DONE_MAX_PIXELS_FROM_CENTER = 5 # TODO - calibrate? there is an optimal number.



############################################################################

class HeadMove(tuple):
    def __init__(self, headYaw, headPitch):
        super(HeadMove, self).__init__((headYaw, headPitch))
    def getHeadYaw(self):
        return self[0]
    def getHeadPitch(self):
        return self[1]

############################################################################

class Tracker(object):
    
    """ track objects by moving the head """
    
    verbose = burst.options.verbose_tracker # turn on for debugging
    debug = verbose and burst.options.debug
    _centering_normalized_x_error = 0.1 # TODO - this should depend on distance?
    _centering_normalized_y_error = 0.1

    def __init__(self, actions):
        self._target = None
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._stop = True
        self._on_lost = None
        self._lost_event = None
        # if _on_centered_bd != None then on centering it is called and tracking
        # is stopped
        self._on_centered_bd = None

        # DEBUG
        #self._trackingStep = traceme(self._trackingStep)

    ############################################################################
    
    def stopped(self):
        return self._stop

    def _start(self, target, on_lost_callback):
        self._target = target
        self._stop = False
        self._on_lost_callback = on_lost_callback
    
    def stop(self):
        """ stop tracker and centered. unregister any events, after
        this call be ready for a new track or center action.
        """
        # don't erase any deferreds here! stop is called
        # before issuing the callbacks, allowing deferred's callee to
        # correctly check that tracker is not operating.
        if self.verbose:
            print "Tracker: Stopping current action - %s" % (
                self._on_centered_bd and 'centering' or 'tracking')
        self._stop = True
        self._on_centered_bd = None

    ############################################################################

    def center(self, target):
        """
        Center on target, returns a BurstDeferred.
        """
        # TODO - what happens if the target is lost during the centering,
        #  but it doesn't have an associated "lost" event? lost can
        # happen because of occlusion, and because of vision problems (which
        # can be minimized maybe).
        if not target.recently_seen: # sanity check (also makes sure we get the
                            # lost event when it happens
            print "ERROR: center called when target not recently in sight"
            #import pdb; pdb.set_trace()
            return
        if self.verbose:
            print "Tracker: Start Centering on %s" % target._name
        self._start(target, self._centeringOnLost)
        self._on_centered_bd = BurstDeferred(None)
        # TODO MAJORLY: This fixes the bug, but real fix is in BurstDeferred
        self._eventmanager.callLater(EVENT_MANAGER_DT, self._centeringStep)
        #self._centeringStep()
        # centering step we are already centered (by calling center twice!)
        return self._on_centered_bd

    def _centeringOnLost(self):
        if not self._target.recently_seen:
            if self.verbose:
                print "Centering: %s not recently seen, continue waiting" % (self._target._name)
        # We can lose the target for a few frames, we can't assume vision is
        # perfect. In this case just wait for next frame.
        # TODO - call callback on too many lost frames. (lost ball, etc - higher up,
        # presumably the Player instance, should deal with this).
        pass

    def _centeringStep(self):
        if self._stop: return
        if not self._target.recently_seen: # TODO - manually looking for lost event. should be event based, no?
            if self.verbose:
                print "CenteringStep: %s not recently seen, calling _on_lost_callback" % self._target._name
            self._onLost()
            return
        if hasattr(self, '_call_me_later'):
            del self._call_me_later
            print "CenteringStep: called later"
        centered, centered_at_pitch_limit, delta_angles, error = self.calculateTracking(self._target,
            normalized_error_x=self._centering_normalized_x_error,
            normalized_error_y=self._centering_normalized_y_error)
        if self.verbose:
            print "CenteringStep: centered = %s, delta_angles %s, centered_at_pitch_limit = %s" % (centered,
                delta_angles or 'is None', centered_at_pitch_limit)
        if centered or centered_at_pitch_limit:
            if self.verbose:
                print "CenteringStep: DONE"
            bd = self._on_centered_bd
            self.stop() # this sets self.on_centered_bd=None
            if bd == None or not bd._ondone or not bd._ondone[0]:
                import pdb; pdb.set_trace()
            if self.debug and bd._ondone and bd._ondone[0]:
                print "CenteringStep: %s" % bd._ondone[0].im_self.__dict__
            bd.callOnDone()
        elif delta_angles:
            # Out path 1: wait for change angles relative to complete
            self._actions.changeHeadAnglesRelative(*delta_angles).onDone(self._centeringStep)
        else:
            print "CenteringStep: callLater"
            # Out path 2: wait a little, try again
            self._call_me_later = 1
            self._eventmanager.callLater(consts.EVENT_MANAGER_DT, self._centeringStep)

    ############################################################################

    def track(self, target, on_lost_callback=None):
        """ Continuous tracking: keep the target in sight.
        """
        # don't track objects that are not seen
        if not target.recently_seen:
            # TODO we immediately call the on_lost_callback - might
            # not be wise - could lead to loops
            if on_lost_callback:
                on_lost_callback()
            return
        if self._on_centered_bd is not None:
            print "ERROR - can't start tracking while centering"
            import pdb; pdb.set_trace()
        self._start(target, on_lost_callback)
        self._on_centered_bd = None
        self._trackingStep()
    
    def _onLost(self):
        self.stop()
        if self._on_lost_callback:
            self._on_lost_callback()
    
    def _trackingStep(self):
        # TODO - we check self._target.seen explicitly, not relying on the
        # self.stop() call in self.onLost (tied to the event_lost), because
        # this avoids the case where this callback is called before the event
        # lost one - how to solve this in a nicer manner?
        if self._stop: return # Stopped
        if self.verbose:
            print "TrackingStep:",
        # check if target is lost, call callback
        if not self._target.recently_seen:
            if self.verbose:
                print "TrackingStep: %s not recently seen, calling _on_lost_callback" % self._target._name
            self._onLost()
            return # Lost target
        centered, maybe_bd = self.executeTracking(self._target)
        if self.verbose:
            print "centered = %s, maybe_bd %s" % (centered,
                not maybe_bd and 'is None' or 'is a deferred')
        # Three possible states:
        if maybe_bd:
            # we initiated a new action - wait for it to complete
            maybe_bd.onDone(self._trackingStep)
        else:
            if not centered:
                # target isn't visible (can be anything - most likely vision has missed it,
                # but could also be occluded, or just moved away quickly, i.e. ball kicked or
                # was in motion to begin with).
                # we don't stop when target is lost - just callLater.
                # TODO - if lost for more then MARGIN tell user?
                if self.verbose:
                    print "TrackingStep: %s not visible right now" % (self._target._name)
            # target is centered or we lost it for a short period (we thing), so just callLater
            #import pdb; pdb.set_trace()
            self._eventmanager.callLater(EVENT_MANAGER_DT, self._trackingStep)

    ### Work horse for actually turning head towards target
    def calculateTracking(self, target,
            normalized_error_x=DEFAULT_CENTERING_X_ERROR,
            normalized_error_y=DEFAULT_CENTERING_Y_ERROR):
        """ This is a controller. Does a single tracking step,
            aiming to center on the given target.

        Return value:
         centerd, maybe_bd, exact_error
         centered - True if centered, False otherwise
         maybe_bd - a BurstDeferred if head movement initiated, else None
         exact_error - the error value (x, y)
        """

        # Need to handle possible out of bounds - if we are requested to
        # go to an elevation that is too high, or to a bearing that is too far
        # left, we need to return success but flag the error for higher up.
        # TODO - handle the out of bounds. Current solution: let higher up
        # handle it. (using same tactic, or check for "noop" for too long)

        delta_angles = None
        centered, centered_at_pitch_limit, xNormalized, yNormalized = target.centering_error(
            normalized_error_x, normalized_error_y)
        head_motion_in_progress = self._world.robot.isHeadMotionInProgress()
        if self.verbose:
            print "Tracker calculation: %s, center %3.1f, %3.1f, error %1.2f, %1.2f" % (
                head_motion_in_progress and 'head moving' or 'head ready',
                target.centerX, target.centerY, xNormalized, yNormalized)
        if target.seen and not centered and not head_motion_in_progress:
            CAM_X_TO_RAD_FACTOR = FOV_X / 4 # do half the error in a single step.
            CAM_Y_TO_RAD_FACTOR = FOV_Y / 4 # TODO - do more then half, or at least set the speed.
            deltaHeadYaw   = -xNormalized * CAM_X_TO_RAD_FACTOR
            deltaHeadPitch =  yNormalized * CAM_Y_TO_RAD_FACTOR
            #self._actions.changeHeadAnglesRelative(
            # deltaHeadYaw * DEG_TO_RAD + self._actions.getAngle("HeadYaw"),
            # deltaHeadPitch * DEG_TO_RAD + self._actions.getAngle("HeadPitch")
            # ) # yaw (left-right) / pitch (up-down)
            delta_angles = (deltaHeadYaw, deltaHeadPitch)
                        # yaw (left-right) / pitch (up-down)
            #print "deltaHeadYaw, deltaHeadPitch (rad): %3.3f, %3.3f" % (
            #       deltaHeadYaw, deltaHeadPitch)
            #print "deltaHeadYaw, deltaHeadPitch (deg): %3.3f, %3.3f" % (
            #       deltaHeadYaw / DEG_TO_RAD, deltaHeadPitch / DEG_TO_RAD)
        return centered, centered_at_pitch_limit, delta_angles, (xNormalized, yNormalized)

    def executeTracking(self, target, normalized_error_x=0.05, normalized_error_y=0.05,
            return_exact_error=False):
        """ Calculate Tracking correction and execute it in a single step. """
        centered, centered_at_pitch_limit, delta_angles, error = self.calculateTracking(target,
            normalized_error_x, normalized_error_y)
        bd = None
        if delta_angles:
            bd = self._actions.changeHeadAnglesRelative(*delta_angles)
        if return_exact_error:
            return centered, bd, error
        return centered, bd

############################################################################

class OldSearcher(object):

    """ Search for a bunch of targets by moving the head (conflicts with Tracker).
    optionally center on each object as a kludge to fix localization right now.

    The results are stored in the target.center of each target.
    """

    def __init__(self, actions):
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._center_on_targets = True
        self._stop = True
        self._targets = []
        self._seen_order = [] # Keeps the actual order targets were seen.
        self._seen_set = set()
        self._events = []
        self._searchlevel = None
        self._timeoutCallback = None
        self.verbose = burst.options.verbose_tracker

    def stopped(self):
        return self._stop

    def stop(self):
        self._unregisterEvents()
        self._stop = True
        self._timeoutCallback = None

    def search(self, targets, center_on_targets=True, timeout=None, timeoutCallback=None):
        '''
        Search fo the objects in /targets/.
        If /center_on_targets/ is True, center on those objects.
        If a /timeout/ is provided, quit the search after that many seconds.
        If a /timeoutCallback/ is provided, call that when and if a timeout occurs.
        '''

        if not timeout is None:
            self._eventmanager.callLater(timeout, self._timeout)
            self._timeoutCallback = timeoutCallback

        if self.verbose:
            print "OldSearcher: Started search for %s" % (', '.join(t._name for t in targets))
        self._targets = targets
        self._center_on_targets = center_on_targets
        del self._seen_order[:]
        self._seen_set.clear()
        self._stop = False

        for target in targets:
            target.centered_self.clear()

        # register to in frame event for each target object
        for obj in targets:
            event = obj.in_frame_event
            callback = lambda obj=obj: self._onSeen(obj)
            self._eventmanager.register(callback, event)
            self._events.append((event, callback))

        # TODO: Fix YELLOW to use opponent goal
        self._searchlevel = burst.actions.LOOKAROUND_QUICK
        self._actions.lookaround(self._searchlevel).onDone(self._onScanDone)

        # create a burst deferred to be called when we found all targets
        self._bd = BurstDeferred(self)
        return self._bd

    def _unregisterEvents(self):
        # should be idempotent
        for event, callback in self._events:
            self._eventmanager.unregister(callback, event)
        self._eventmanager.cancelCallLater(self._timeout)
        del self._events[:]

    def _timeout(self):
        """ called using callLater if timeout requested """
        if not self.stopped():
            if not self._timeoutCallback is None:
                self._timeoutCallback()
            self.stop()

    def _onOneCentered(self):
        target = self._center_target
        if self.verbose:
            print "OldSearcher: Center: %s centering done (updated by standard calc_events)" % target._name
        self._centerOnNext()

    def _centerOnNext(self):
        # need to first go to a close place, use angles last seen
        # TODO - use median of last seen angles, would be much closer
        # to reality
        try:
            self._center_target = target = self._center_targets.next()
        except StopIteration:
            #import pdb; pdb.set_trace()
            if self.verbose:
                print "CenterOnNext: DONE"
            self._onFinishedScanning()
            return

        c_target = target.centered_self
        if self.verbose:
            print "OldSearcher: moving towards and centering on %s - (%1.2f, %1.2f)" % (
                target._name, c_target.head_yaw, c_target.head_pitch)
        # Actually that head_yaw / head_pitch is suboptimal. We have also centerX and
        # centerY, it is trivial to add them to get a better estimate for the center,
        # still calling center afterwards.
        a1 = c_target.head_yaw, c_target.head_pitch
        a2 = (a1[0] - PIX_TO_RAD_X * (c_target.centerX - IMAGE_CENTER_X),
              a1[1] + PIX_TO_RAD_Y * (c_target.centerY - IMAGE_CENTER_Y))
        #nodding = a1, a2, a1, a2
        #bd = self._actions.chainHeads(nodding)
        bd = self._actions.moveHead(*a2)
        # target.centered_self is updated every step, we just need to do the centering head move.
        return bd.onDone(lambda _, target=target: self._actions.tracker.center(target)
                ).onDone(self._onOneCentered)

    def _onScanDone(self):
        if self._stop: return
        
        # see which targets have been sighted
        seen = set(target for target in self._targets if target.centered_self.sighted)
        unseen = set(target for target in self._targets if not target.centered_self.sighted)
        if self.verbose:
            print "Seen = #%d, Targets = #%d" % (len(seen), len(self._targets))
        if len(seen) == len(self._targets):
            # best case - all done
            self._unregisterEvents()
            if self._center_on_targets:
                # center on every target by reverse order of seen
                # TODO - chainDeferred would have been nicer (a list
                # instead of a 'lisp list' to represent the future)
                # but there is a bug with my getDeferred in context of chainDeferreds
                self._center_targets = reversed(self._seen_order)
                self._centerOnNext()
            else:
                self._onFinishedScanning()
        else:
            bd = self._runSpecializedStrategy(seen, unseen)
            if bd:
                if self.verbose:
                    print "OldSearcher: using specialized strategy for (seen %r, unseen %r)" % (
                        [t._name for t in seen], [t._name for t in unseen])
            else:
                if self.verbose:
                    print "OldSearcher: targets {%s} NOT seen, searching again..." % (','.join(obj._name for obj in unseen))
                self._searchlevel = (self._searchlevel + 1) % burst.actions.LOOKAROUND_MAX
                bd = self._actions.lookaround(self._searchlevel)
            bd.onDone(self._onScanDone)

    def _runSpecializedStrategy(self, seen, unseen):
        """ place to register any interesting strategy concerning the
        matrix of 2^{#targets} x 2^{#targets}. Used right now for
        any case where we missed one post but saw it's twin

        return None if we don't have a special strategy.
        """
        # TODO - specialized strategies fail, then what? should go back to overall scan.
        world = self._world
        yellow_bot, yellow_top, blue_bot, blue_top = (
            world.yglp, world.ygrp, world.bgrp, world.bglp)
        R, L = consts.joint_limits['HeadYaw'][:2]
        pitch = self._world.getAngle('HeadPitch')
        for yaw, s, u in [( L, yellow_bot, yellow_top), ( R, yellow_top, yellow_bot),
                          ( R, blue_bot, blue_top), ( L, blue_top, blue_bot)]:
            if s in seen and u in unseen:
                return self._actions.moveHead(yaw, pitch)
        return None

    def _onFinishedScanning(self):
        if self.verbose:
            print "OldSearcher: DONE"
        self.stop()
        self._bd.callOnDone()

    def _onSeen(self, target):
        if self._stop: return
        if not target.seen or not target.dist:
            if self.verbose:
                print "OldSearcher: onSeen but target seen=%r and dist=%r" % (target.seen, target.dist)
            return
        # TODO OPTIMIZATION - when last target is seen, cut the search
        #  - stop current move
        #  - call _onScanDone to start centering.
        if target not in self._seen_set:
            if self.verbose:
                print "OldSearcher: First Sighting: %s, dist = %s, centered: %s" % (target._name, target.dist, target.centered_self)
            self._seen_order.append(target)
            self._seen_set.add(target)

############################################################################

def createNewSearchMovesIterator(searcher):

    class HeadMovementCommand(object):
        def __init__(self, headYaw, headPitch):
            self.headYaw = headYaw
            self.headPitch = headPitch
        def __call__(self):
            return searcher._actions.moveHead(self.headYaw, self.headPitch)

    class TurnCommand(object):
        def __init__(self, thetadelta):
            self.thetadelta = thetadelta
        def __call__(self):
            return searcher._actions.turn(self.thetadelta)

    def iterator(searcher=searcher):
        while True:
            for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (-1.0, 0.5), (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
                yield HeadMovementCommand(*headCoordinates)
            yield TurnCommand(-pi/2)

    return iterator()

# TODO: Have the head turned the way we're turning. # Setting pi/2 to -pi/2 should have solved this, for now.
# TODO: Clear foot steps if found while turning.
# TODO: More efficient head movements (speed).
# TODO: More efficient head movements (order).

############################################################################

class Searcher(object):

    def __init__(self, actions):
        self.verbose = burst.options.verbose_tracker
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self.reset()

    def reset(self):
        self._stopped = True # TODO: For timeouts, use an "ack".
        self._timeoutCallback = None
        self._seen_objects = []
        self._callbackToEventMapping = []
        self._searchMoves = None
        self._deferred = None

    def stopped(self):
        return self._stopped

    def stop(self):
        self._unregisterEvents()
        self.reset()

    def search(self, targets, center_on_targets=True, timeout=None, timeoutCallback=None):
        '''
        Search fo the objects in /targets/.
        If /center_on_targets/ is True, center on those objects.
        If a /timeout/ is provided, quit the search after that many seconds.
        If a /timeoutCallback/ is provided, call that when and if a timeout occurs.
        '''

        self.targets = targets[:]
        self.center_on_targets = center_on_targets
        self._timeoutCallback = timeoutCallback

        # Forget where you've previously seen these objects - you wouldn't be looking for them if they were still there.
        for target in targets:
            target.centered_self.clear()

        # Register for the timeout, if one has been asked for.
        if not timeout is None:
            self._eventmanager.callLater(timeout, self._onTimeout)

        # For each target you are searching for, have a callback lined up for the event of seeing it.
        for target in targets:
            callback = lambda obj=target: self._onSeen(obj)
            event = target.in_frame_event
            self._eventmanager.register(callback, event)
            self._callbackToEventMapping.append((callback, event))

        # Launch the search, according to some search strategy.
        self._searchMoves = createNewSearchMovesIterator(self) # TODO: Give that function the world+search state, so it makes informed decisions.
        self._nextSearchMove()

        # Return a promise to call when done. Remember that registration to a timeout is done during the calling of this function.
        self._deferred = BurstDeferred(self)
        return self._deferred

    def _unregisterEvents(self):
        ''' Unregisters all the requests for callbacks this object has, as well as the timeout, if one exists. '''
        for callback, event in self._callbackToEventMapping:
           self._eventmanager.unregister(callback, event)
        if not self._timeoutCallback is None:
            self._eventmanager.cancelCallLater(self._timeoutCallback)

    def _onSeen(self, obj):
        if self.verbose:
            print "Searcher: seeing %s" % obj._name
        if not obj in self._seen_objects:
            # TODO: Remove the registration for this event?
            self._seen_objects.append(obj)
            if self._seenAll():
                self._onSeenAll()

    # TODO: Make the iterator return something more general (a command pattern), so that not only head movements are supported, but the whole body.
    # TODO: Alon, notice that the previous TODO has been accomplished, and is another benefit.
    def _nextSearchMove(self):
        try:
            self._searchMoves.next().__call__().onDone(self._nextSearchMove)
        except StopIteration:
            raise Exception("Search iterators are expected to be never-ending.")

    def _seenAll(self):
        for target in self.targets:
            if not target in self._seen_objects:
                return False
        return True

    def _onSeenAll(self):
        if self.verbose:
            print "Searcher: found all targets"
        deferred = self._deferred
        self.stop()
        deferred.callOnDone()

    def _onTimeout(self):
        if not self.stopped():
            timeoutCallback = self._timeoutCallback
            self.stop()
            if not timeoutCallback is None:
                timeoutCallback()

