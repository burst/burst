import sys
import linecache

from burst_util import (traceme, nicefloat,
    Deferred, chainDeferreds)
from burst.events import *
import burst
import burst_consts as consts
from burst_consts import (FOV_X, FOV_Y, EVENT_MANAGER_DT,
    DEFAULT_NORMALIZED_CENTERING_X_ERROR,
    DEFAULT_NORMALIZED_CENTERING_Y_ERROR, PIX_TO_RAD_X, PIX_TO_RAD_Y,
    IMAGE_CENTER_X, IMAGE_CENTER_Y)
import burst.events as events
from burst.image import normalized2_image_width, normalized2_image_height
from math import pi

############################################################################

class Tracker(object):
    
    """ track objects by moving the head """
    
    def __init__(self, actions):
        self._target = None
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._stopped = True
        self._on_lost = None
        self._lost_event = None
        # if _on_centered_bd != None then on centering it is called and tracking
        # is stopped
        self._on_centered_bd = None

        self.verbose = burst.options.verbose_tracker # turn on for debugging
        self.debug = self.verbose and burst.options.debug
        self._centering_normalized_x_error = 0.1 # TODO - this should depend on distance?
        self._centering_normalized_y_error = 0.1


        # DEBUG
        #self._trackingStep = traceme(self._trackingStep)

    ############################################################################
    
    def _start(self, target, on_lost_callback):
        self._target = target
        self._stopped = False
        self._on_lost_callback = on_lost_callback

    def stopped(self):
        return self._stopped

    def stop(self):
        """ stop tracker and centered. unregister any events, after
        this call be ready for a new track or center action.
        """
        # don't erase any deferreds here! stop is called
        # before issuing the callbacks, allowing deferred's callee to
        # correctly check that tracker is not operating.
        if self.stopped(): return
        if self.verbose:
            print "Tracker: Stopping current action - %s" % (
                self._on_centered_bd and 'centering' or 'tracking')
        self._stopped = True
        self._on_centered_bd = None
        self._user_on_lost = None
        self._user_on_timeout = None
        self._timeout = None

    ############################################################################

    def center(self, target, lostCallback=None, timeout=None, timeoutCallback=None):
        """
        Center on target, returns a BurstDeferred.
        """
        # TODO - what happens if the target is lost during the centering,
        #  but it doesn't have an associated "lost" event? lost can
        # happen because of occlusion, and because of vision problems (which
        # can be minimized maybe).
        '''
        if not target.recently_seen: # don't start centering on a target that isn't visible
            print "ERROR: center called when target not recently in sight"
            return
        '''
        if self.verbose:
            print "Tracker: Start Centering on %s" % target.name
        self._on_centered_bd = self._actions.burst_deferred_maker.make(self)
        self._start(target, lostCallback or self._on_centered_bd.callOnDone)
        # TODO MAJORLY: This fixes the bug, but real fix is in BurstDeferred
        self._eventmanager.callLater(EVENT_MANAGER_DT, self._centeringStep)
        self._timeout = timeout
        self._user_on_timeout = timeoutCallback or self._on_centered_bd.callOnDone
        if timeout:
            self._eventmanager.callLater(timeout, self._centeringOnTimeout)
        #self._centeringStep()
        # centering step we are already centered (by calling center twice!)
        return self._on_centered_bd

    def _centeringOnTimeout(self):
        if self.verbose:
            print "Tracking: Centering: Timeout (%s)" % (self._timeout)
        user_cb = self._user_on_timeout
        self.stop()
        if user_cb:
            user_cb()

    def _centeringStep(self):
        if self._stopped: return
        if not self._target.recently_seen:
            if self.verbose:
                print "CenteringStep: %s not recently seen, calling _on_lost_callback" % self._target.name
            self._onLost()
            return
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
                print "CenteringStep: pdb - no callback set on bd"
                import pdb; pdb.set_trace()
            if self.debug and bd._ondone and bd._ondone[0]:
                print "CenteringStep: %s" % bd._ondone[0].im_self.__dict__
            bd.callOnDone()
        elif delta_angles:
            # Out path 1: wait for change angles relative to complete
            self._actions.changeHeadAnglesRelative(*delta_angles).onDone(self._centeringStep)
        else: # target.recently_seen is True
            # Out path 2: wait a little, try again
            self._eventmanager.callLater(consts.EVENT_MANAGER_DT, self._centeringStep)

    ############################################################################

    def track(self, target, lostCallback=None):
        """ Continuous tracking: keep the target in sight.
        """
        # Check for conflicting actions
        if not self._actions.searcher.stopped():
            print "Tracker: ERROR: Track while Search"
            import pdb; pdb.set_trace()
        if self._on_centered_bd is not None:
            print "ERROR - can't start tracking while centering"
            import pdb; pdb.set_trace()
        
        # don't track objects that are not seen
        if not target.recently_seen:
            # TODO we immediately call the on_lost_callback - might
            # not be wise - could lead to loops
            if lostCallback:
                lostCallback()
            return
        self._start(target, lostCallback)
        self._on_centered_bd = None
        self._trackingStep()
    
    def _onLost(self):
        on_lost_cb = self._on_lost_callback
        self.stop()
        if on_lost_cb:
            on_lost_cb()
    
    def _trackingStep(self):
        # TODO - we check self._target.seen explicitly, not relying on the
        # self.stop() call in self.onLost (tied to the event_lost), because
        # this avoids the case where this callback is called before the event
        # lost one - how to solve this in a nicer manner?
        if self._stopped: return # Stopped
        if self.verbose:
            print "TrackingStep:",
        # check if target is lost, call callback
        if not self._target.recently_seen:
            if self.verbose:
                print "TrackingStep: %s not recently seen, calling _on_lost_callback" % self._target.name
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
                    print "TrackingStep: %s not visible right now" % (self._target.name)
            # target is centered or we lost it for a short period (we thing), so just callLater
            #import pdb; pdb.set_trace()
            self._eventmanager.callLater(EVENT_MANAGER_DT, self._trackingStep)

    ### Work horse for actually turning head towards target
    def calculateTracking(self, target,
            normalized_error_x=DEFAULT_NORMALIZED_CENTERING_X_ERROR,
            normalized_error_y=DEFAULT_NORMALIZED_CENTERING_Y_ERROR):
        """ This is a controller. Does a single tracking step,
            aiming to center on the given target.

        Return value:
         centerd, maybe_bd, exact_error
         centered - True if centered, False otherwise
         delta_angles - None if no move possible (target is not visible), otherwise correction.
         (xNormalized, yNormalized) - error
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
        if self.verbose:
            angles = (delta_angles and ', angles (%1.2f %1.2f)' % delta_angles) or ''
            print "Tracker calculation: %s, center %3.1f, %3.1f, error (%1.2f, %1.2f)%s" % (
                head_motion_in_progress and 'head moving' or 'head ready',
                target.centerX, target.centerY, xNormalized, yNormalized, angles)
        return centered, centered_at_pitch_limit, delta_angles, (xNormalized, yNormalized)

    def executeTracking(self, target, normalized_error_x=0.05, normalized_error_y=0.05,
            return_exact_error=False):
        """ Calculate Tracking correction and execute it in a single step. """
        centered, centered_at_pitch_limit, delta_angles, error = self.calculateTracking(target,
            normalized_error_x, normalized_error_y)
        bd = None
        if delta_angles:
            if self.verbose:
                print "Tracker: change angles by yaw=%1.2f, pitch=%1.2f" % delta_angles
            bd = self._actions.changeHeadAnglesRelative(*delta_angles)
        if return_exact_error:
            return centered, bd, error
        return centered, bd

############################################################################

# TODO - keep actions instead of searcher? who else would use
# these commands? too many "smart" ways to connect actions, makes it /harder/
# to concoct elequent 'just complex enough' behaviors

class HeadMovementCommand(object):

    def __init__(self, actions, headYaw, headPitch):
        self._actions = actions
        self.headYaw = headYaw
        self.headPitch = headPitch

    def __call__(self):
        return self._actions.moveHead(self.headYaw, self.headPitch)

class CenteringCommand(object):

    """ Turn towards an initial position, then execute centering
    a few times, each time using the most centered position currently
    known to bootstrap."""
    

    def __init__(self, actions, headYaw, headPitch, target, repeats=2):
        """ repeats - number of times to run centering. First time the
        target is centered, or if repeats times pass, we call the bd returned
        """
        self._actions = actions
        self._yaw, self._pitch, self._target = headYaw, headPitch, target
        self._repeats = repeats

    def onCenteringDone(self):
        # called both on centering and on target lost
        if self._target.sighted_centered or self._repeats == 0:
            self._bd.callOnDone()
        print "CENTERING %s" % self._repeats
        self._repeats -= 1
        new_yaw, new_pitch = self._target.centered_self.estimated_yaw_and_pitch_to_center()
        self._actions.moveHead(new_yaw, new_pitch).onDone(
            lambda: self._actions.tracker.center(self._target).onDone(self.centeringDone)
        )
            
    def __call__(self):
        self._bd = bd = self._actions.moveHead(self._yaw, self._pitch)
        # TODO - testing. Does this actually call the right bd?
        # maybe switch to Deferreds here, since they are much
        # simpler compared to the BurstDeferred chain thing?
        bd.onDone(self.onCenteringDone)
        return bd

class TurnCommand(object):

    def __init__(self, actions, thetadelta):
        self._actions = actions
        self.thetadelta = thetadelta

    def __call__(self):
        return self._actions.turn(self.thetadelta)

class SwitchCameraCommand(object):

    def __init__(self, actions, whichCamera):
        self.actions = actions
        self.whichCamera = whichCamera

    def __call__(self):
        return self.actions.setCamera(self.whichCamera)

def baseIter(searcher):
    while True:
#        if not searcher._actions.currentCamera == consts.CAMERA_WHICH_BOTTOM_CAMERA:
#            yield SwitchCameraCommand(searcher._actions, consts.CAMERA_WHICH_BOTTOM_CAMERA)
        for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (-1.0, 0.5), (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
            yield HeadMovementCommand(searcher._actions, *headCoordinates)
#        yield SwitchCameraCommand(searcher._actions, consts.CAMERA_WHICH_TOP_CAMERA)
#        for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (-1.0, 0.5), (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
#            yield HeadMovementCommand(searcher._actions, *headCoordinates)
        yield TurnCommand(searcher._actions, -pi/2)

class SearchPlanner(object):

    """ The planner determines the next actions, but the searcher
    takes care of the seen events. There is a slight breaking in this
    pattern when we center on targets - then temporarily the tracker
    takes care of both actions and seen events """

    def __init__(self, searcher, center=False, _baseIter=baseIter):
        self.verbose = burst.options.verbose_tracker
        self._searcher = searcher
        self._baseIter = _baseIter(searcher)
        self._nextTargets = []
#            self._lastPosition = searcher.self. # TODO: return to the last position after a chain of targets.
        if center:
            self._centerCommand = CenteringCommand
        else:
            self._centerCommand = (lambda actions, yaw, pitch, target:
                HeadMovementCommand(actions, yaw, pitch))

    def feedNext(self, target):
        self._nextTargets.append(target)

    def next(self):
        if len(self._nextTargets) == 0:
            self._report("giving a command according to the base-iterator.")
            return self._baseIter.next()
        else:
            target = self._nextTargets[0]
            del self._nextTargets[0]
            self._report("giving a centering command: %s" % target.name)
            yaw, pitch = target.centered_self.estimated_yaw_and_pitch_to_center()
            return self._centerCommand(self._searcher._actions, yaw, pitch, target)

    def hasMoreCenteringTargets(self):
        return self._nextTargets != []

    def _report(self, string):
        if self.verbose:
            print "Planner: %s" % string

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
        self._search_count = [0, 0] # starts, stops
        self._reset()
        self._stopped = True
        # this is the default "did I see all targets" function, used
        # by searchHelper to provide both "all" and "one off" behavior.
        self._seenTargets = self._seenAll

    def _reset(self):
        self._timeoutCallback = None
        self.seen_objects = []
        self._eventToCallbackMapping = {}
        self._searchMoves = None
        self._deferred = None
        self.targets = []
        self._report("Searcher: RESET")

    def _report(self, *strings):
        if self.verbose:
            print "Searcher: %s: %s" % (self._search_count, '\n'.join(strings))

    def stopped(self):
        return self._stopped

    def stop(self):
        if self.stopped(): return
        self._unregisterAllEvents()
        self._search_count[1] += 1
        self._stopped = True
        self._report("Searcher: STOPPED")

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
        if not self.stopped():
            print "Searcher: WARNING: starting new search but not stopped"
            import pdb; pdb.set_trace()
        self._reset()
        self._stopped = False
        self._search_count[0] += 1
        self._report("Searcher: search started for %s. %s, %s" % (','.join([t.name for t in targets]),
            center_on_targets and 'with centering' or 'no centering',
            self._seenTargets == self._seenAll and 'for all' or 'for one'))
        self.targets = targets[:]
        self._center_on_targets = center_on_targets
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
        self._searchPlanner = SearchPlanner(self, center_on_targets) # TODO: Give that function the world+search state, so it makes informed decisions.
        self._eventmanager.callLater(0, self._nextSearchMove) # The centered_selves have just been cleared. # TODO: Necessary.

        # shortcut if we already see some or all of the targets
        for target in self.targets:
            if target.seen:
                self._onSeen(target, target.in_frame_event) # TODO - recently_seen?

        # Return a promise to call when done. Remember that registration to a timeout is done during the calling of this function.
        self._deferred = self._actions.burst_deferred_maker.make(self)
        assert(self._deferred)
        return self._deferred

    def _unregisterSeenEvents(self):
        ''' Unregisters all the requests for callbacks this object has, as well as the timeout, if one exists. '''
        self._report("Searcher: unregistering seen events: %s" % str(self._eventToCallbackMapping.keys()))
        for event, callback in self._eventToCallbackMapping.items():
            self._eventmanager.unregister(callback, event)
        self._eventToCallbackMapping.clear()

    def _unregisterAllEvents(self):
        ''' Unregisters all the requests for callbacks this object has, as well as the timeout, if one exists. '''
        self._unregisterSeenEvents()
        if not self._timeoutCallback is None:
            self._eventmanager.cancelCallLater(self._timeoutCallback)

    def _onSeen(self, obj, event):
        self._report("Searcher: seeing %s" % obj.name)
#            print "\nSearcher seeing ball?: (ball seen %s, ball recently seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (
#                self._world.ball.seen, self._world.ball.recently_seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)

        #if len(self._eventToCallbackMapping) == 0: return
        if not obj in self.seen_objects:
            self._report("Searcher: first time seen %s" % obj.name)
            #self._eventmanager.unregister(self._onSeen, event)
            if event in self._eventToCallbackMapping:
                self._report("Searcher: unregistering %s (%s)" % (event, events.event_name(event)))
                cb = self._eventToCallbackMapping[event]
                self._eventmanager.unregister(cb, event)
                del self._eventToCallbackMapping[event]
            self.seen_objects.append(obj)
            if self._center_on_targets:
                self._report("Next, I'll center on %s" % obj.name)
                self._searchPlanner.feedNext(obj)

    def _nextSearchMove(self):
        ''' Whenever a movement is finished, either the search is done, or a new movement should be issued. '''
        if not self.stopped():
            if not self._seenTargets() or self._searchPlanner.hasMoreCenteringTargets():
                try:
                    self._searchPlanner.next().__call__().onDone(self._nextSearchMove)
                    self._report("%s, %s" % (self.targets,
                        self._searchPlanner.hasMoreCenteringTargets() and 'has more centering targets' or 'done centering'))
                except StopIteration:
                    raise Exception("Search iterators are expected to be never-ending.")
            else:
                self._onSearchDone()

    def _seenOne(self):
        """ function for search_one_of, checks if one of the supplied targets
        has been seen """
        self._report("_seenOne: len(self.seen_objects) = %s" % len(self.seen_objects))
        return len(self.seen_objects) >= 1

    def _seenAll(self):
        """ default _seenTargets function, checks that all
        targets have been seen """
        for target in self.targets:
            if not target in self.seen_objects:
                self._report("_seenAll FALSE")
                return False
        self._report("_seenAll TRUE")
        return True

    def _onSearchDone(self):
        ''' Wrapping up once a search has been successfully completed. '''
        if self.stopped():
            print "Searcher: WARNING! self.stopped() is TRUE"
            return
        deferred = self._deferred
        self.stop()
        deferred.callOnDone()

    def _onTimeout(self):
        ''' The event for a searching having timed-out. '''
        if not self.stopped():
            timeoutCallback = self._timeoutCallback
            self.stop()
            if not timeoutCallback is None:
                timeoutCallback()

