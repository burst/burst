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
import burst.events as events
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
        '''
        if not target.recently_seen: # sanity check (also makes sure we get the
                            # lost event when it happens
            print "ERROR: center called when target not recently in sight"
            #import pdb; pdb.set_trace()
            return
        '''
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
            '''
            self._onLost()
            return
            '''
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

UGLY = 0 # TODO: Remove this debugging line.

def createNewSearchMovesIterator(searcher):

    class HeadMovementCommand(object):
        def __init__(self, headYaw, headPitch):
            self.headYaw = headYaw
            self.headPitch = headPitch
        def __call__(self):
            # XXX: shouldn't we also pass the interp_time parameter?
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
# TODO: Center while searching, so that you can move freely about.

############################################################################

class Searcher(object):

    def __init__(self, actions):
        self.verbose = burst.options.verbose_tracker
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self.reset()
        # this is the default "did I see all targets" function, used
        # by searchHelper to provide both "all" and "one off" behavior.
        self._seenTargets = self._seenAll

    def reset(self):
        self._stopped = True # TODO: For timeouts, use an "ack".
        self._timeoutCallback = None
        self._seen_objects = []
        self._eventToCallbackMapping = {}
        self._searchMoves = None
        self._deferred = None
        self._targets = []

    def stopped(self):
        return self._stopped

    def stop(self):
        if self.verbose:
            print "Searcher: STOPPING"
        self._unregisterAllEvents()
        self.reset()

    def search_one_of(self, targets, center_on_targets=True, timeout=None, timeoutCallback=None):
        self._seenTargets = self._seenOne
        return self._searchHelper(targets, center_on_targets, timeout, timeoutCallback)

    def search(self, targets, center_on_targets=True, timeout=None, timeoutCallback=None):
        self._seenTargets = self._seenAll
        return self._searchHelper(targets, center_on_targets, timeout, timeoutCallback)

    def _searchHelper(self, targets, center_on_targets, timeout, timeoutCallback):
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
            event = target.in_frame_event
            callback = lambda obj=target, event=event: self._onSeen(obj, event)
            self._eventmanager.register(callback, event)
            self._eventToCallbackMapping[event] = callback

        # Launch the search, according to some search strategy.
        self._searchMoves = createNewSearchMovesIterator(self) # TODO: Give that function the world+search state, so it makes informed decisions.
        self._nextSearchMove()

        # Return a promise to call when done. Remember that registration to a timeout is done during the calling of this function.
        self._deferred = BurstDeferred(self)
        return self._deferred

    def _unregisterSeenEvents(self):
        ''' Unregisters all the requests for callbacks this object has, as well as the timeout, if one exists. '''
        if self.verbose:
            print "Searcher: unregistering seen events: %s" % str(self._eventToCallbackMapping.keys())
        for event, callback in self._eventToCallbackMapping.items():
           self._eventmanager.unregister(callback, event)
        self._eventToCallbackMapping.clear()

    def _unregisterAllEvents(self):
        ''' Unregisters all the requests for callbacks this object has, as well as the timeout, if one exists. '''
        self._unregisterSeenEvents()
        if not self._timeoutCallback is None:
            self._eventmanager.cancelCallLater(self._timeoutCallback)

    def _onSeen(self, obj, event):
        if self.verbose:
            print "Searcher: seeing %s" % obj._name
#            print "\nSearcher seeing ball?: (ball seen %s, ball recently seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (
#                self._world.ball.seen, self._world.ball.recently_seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)

        #if len(self._eventToCallbackMapping) == 0: return
        if not obj in self._seen_objects:
            if self.verbose:
                print "Searcher: first time seen %s" % obj._name
            #self._eventmanager.unregister(self._onSeen, event)
            if event in self._eventToCallbackMapping:
                if self.verbose:
                    print "Searcher: unregistering %s (%s)" % (event, events.event_name(event))
                cb = self._eventToCallbackMapping[event]
                self._eventmanager.unregister(cb, event)
                del self._eventToCallbackMapping[event]
            self._seen_objects.append(obj)

    # TODO: Make the iterator return something more general (a command pattern), so that not only head movements are supported, but the whole body.
    # TODO: Alon, notice that the previous TODO has been accomplished, and is another benefit.
    def _nextSearchMove(self):
        if self.verbose:
            print "Searcher: _nextSearchMove()"
        if self._seenTargets():
            return self._onSeenTargets()
        try:
            # XXX: prevents cases where self._searchMoves is None and so next() can't be called...
            #      we probably need better solution...
            if not self._searchMoves is None:
                self._searchMoves.next().__call__().onDone(self._nextSearchMove)
        except StopIteration:
            raise Exception("Search iterators are expected to be never-ending.")

    def _seenOne(self):
        """ function for search_one_of, checks if one of the supplied targets
        has been seen """
        if self.verbose:
            print "_seenOne: %f" % len(self._seen_objects)
        return len(self._seen_objects) >= 1

    def _seenAll(self):
        """ default _seenTargets function, checks that all
        targets have been seen """
        for target in self.targets:
            if not target in self._seen_objects:
                if self.verbose:
                    print "_seenAll FALSE"
                return False
        if self.verbose:
            print "_seenAll TRUE"
        return True

    def _onSeenTargets(self):
        if self.verbose:
            print "Searcher: found all targets"
            print "len(self._seen_objects): %f" % len(self._seen_objects)
        if not self.center_on_targets:
            self._onSearchDone()
        else:
            self._unregisterSeenEvents()
            self._moveTowardsNextTarget()

    def _moveTowardsNextTarget(self):
        if len(self._seen_objects) == 0:
            self._onSearchDone()
        else:
            target = self._seen_objects.pop()
            if self.verbose:
                print "Searcher: centering on %s" % target._name
            yaw = target.centered_self.head_yaw - PIX_TO_RAD_X * (target.centered_self.centerX - IMAGE_CENTER_X)
            pitch = target.centered_self.head_pitch + PIX_TO_RAD_Y * (target.centered_self.centerY - IMAGE_CENTER_Y)
            self._actions.moveHead(yaw, pitch).onDone(lambda target=target: self._centerOnNextTarget(target))

    def _centerOnNextTarget(self, target):
        self._moveTowardsNextTarget() # TODO: Remove.
#        self._actions.tracker.center(target).onDone(self._moveTowardsNextTarget)

    def _onSearchDone(self):
        deferred = self._deferred
        self.stop()
        deferred.callOnDone()

    def _onTimeout(self):
        if not self.stopped():
            timeoutCallback = self._timeoutCallback
            self.stop()
            if not timeoutCallback is None:
                timeoutCallback()

