import sys
import linecache
from textwrap import wrap

from burst_util import (traceme, nicefloat,
    BurstDeferred, Deferred, chainDeferreds)
from burst.events import *
import burst
import burst_consts as consts
from burst_consts import (FOV_X, FOV_Y, EVENT_MANAGER_DT,
    CONSOLE_LINE_LENGTH, DEFAULT_CENTERING_X_ERROR,
    DEFAULT_CENTERING_Y_ERROR)
from burst.image import normalized2_image_width, normalized2_image_height

# This is used for stuff like Localization, where there is an error
# that is reduced by having a smaller error - otoh tracker will take longer
# (possibly)
TRACKER_DONE_MAX_PIXELS_FROM_CENTER = 5 # TODO - calibrate? there is an optimal number.

class Tracker(object):
    
    """ track objects by moving the head """
    
    verbose = burst.options.verbose_tracker # turn on for debugging
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
        # if _centering_done != None then on centering it is called and tracking
        # is stopped
        self._centering_done = None

        # DEBUG
        #self._trackingStep = traceme(self._trackingStep)

    ############################################################################
    
    def stopped(self):
        return self._stop

    def _start(self, target, on_lost_callback):
        self._target = target
        self._stop = False
        if hasattr(target, 'lost_event'):
            self._lost_event = target.lost_event
            if on_lost_callback:
                self._on_lost = BurstDeferred(self)
                self._on_lost.onDone(on_lost_callback)
            self._eventmanager.register(self.onLost, self._lost_event)

    def onLost(self):
        self.stop()
        if self._on_lost:
            self._on_lost.callOnDone()
    
    def stop(self):
        """ stop tracker and centerred. unregister any events, after
        this call be ready for a new track or center action.
        """
        # don't erase any deferreds here! stop is called
        # before issuing the callbacks, allowing deferred's callee to
        # correctly check that tracker is not operating.
        if self.verbose:
            print "Tracker: Stopping current action - %s" % (
                self._centering_done and 'centering' or 'tracking')
        self._stop = True
        self._centering_done = None
        if self._lost_event: # can be None
            self._eventmanager.unregister(self.onLost, self._lost_event)

    ############################################################################

    def center(self, target):
        """
        Center on target, returns a BurstDeferred.
        """
        # TODO - what happens if the target is lost during the centerring,
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
        self._centering_done = BurstDeferred(None)
        self._centeringStep()
        # TODO: check that this works correctly if on the first
        # centering step we are already centered (by calling center twice!)
        return self._centering_done

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
            self.onLost()
        if hasattr(self, '_call_me_later'):
            del self._call_me_later
            print "CenteringStep: called later"
        centered, delta_angles, error = self.calculateTracking(self._target,
            normalized_error_x=self._centering_normalized_x_error,
            normalized_error_y=self._centering_normalized_y_error)
        elevation_on_upper_edge = (self._world.getAngle('HeadPitch') < consts.joint_limits['HeadPitch'][0]*0.99)
        center_too_high = elevation_on_upper_edge and error[1] < 0
        if self.verbose:
            print "CenteringStep: centered = %s, delta_angles %s, center_too_high = %s" % (centered,
                delta_angles or 'is None', center_too_high)
        if centered or (
            abs(error[0]) < self._centering_normalized_x_error and center_too_high):
            if self.verbose:
                print "CenteringStep: DONE"
            bd = self._centering_done
            self.stop() # this sets self.centering_done=None
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
        if not target.seen:
            # TODO we immediately call the on_lost_callback - might
            # not be wise - could lead to loops
            if on_lost_callback:
                on_lost_callback()
            return
        if self._centering_done is not None:
            print "ERROR - can't start tracking while centering"
            import pdb; pdb.set_trace()
        self._start(target, on_lost_callback)
        self._centering_done = None
        self._trackingStep()
    
    def _trackingStep(self):
        # TODO - we check self._target.seen explicitly, not relying on the
        # self.stop() call in self.onLost (tied to the event_lost), because
        # this avoids the case where this callback is called before the event
        # lost one - how to solve this in a nicer manner?
        if self._stop: return
        if self.verbose:
            print "TrackingStep:",
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
                # but could also be ocluded, or just moved away quickly, i.e. ball kicked or
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
        centered, xNormalized, yNormalized = target.centering_error(
            normalized_error_x, normalized_error_y)
        head_motion_in_progress = self._world.robot.isHeadMotionInProgress()
        if self.verbose:
            print "Tracker calculation: %s, center %3.1f, %3.1f, error %1.2f, %1.2f" % (
                head_motion_in_progress and 'head moving' or 'head ready',
                target.centerX, target.centerY, xNormalized, yNormalized)
        if target.seen and not centered and not head_motion_in_progress:
            CAM_X_TO_RAD_FACTOR = FOV_X / 4 # TODO - const that 1/4 ?
            CAM_Y_TO_RAD_FACTOR = FOV_Y / 4
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
        return centered, delta_angles, (xNormalized, yNormalized)

    def executeTracking(self, target, normalized_error_x=0.05, normalized_error_y=0.05,
            return_exact_error=False):
        """ Calculate Tracking correction and execute it in a single step. """
        centered, delta_angles, error = self.calculateTracking(target,
            normalized_error_x, normalized_error_y)
        bd = None
        if delta_angles:
            bd = self._actions.changeHeadAnglesRelative(*delta_angles)
        if return_exact_error:
            return centered, bd, error
        return centered, bd

############################################################################

class SearchResults(object):
    
    def __init__(self):
        # 3d based estimates
        self.elevation, self.dist, self.bearing = None, None, None
        # image based
        self.centerX, self.centerY = None, None
        self.normalized2_centerX, self.normalized2_centerY = None, None
        # 
        self.sighted = False

    def __str__(self):
        return '\n'.join(wrap('{%s}' % (', '.join(('%s:%s' % (k, nicefloat(v))) for k, v in self.__dict__.items() )), CONSOLE_LINE_LENGTH))

############################################################################

class Searcher(object):
    
    """ search for a bunch of targets by moving the head (conflicts with Tracker) """
    
    verbose = burst.options.verbose_tracker

    def __init__(self, actions):
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._searchlevel = None
        self._targets = []
        self._seen_order = [] # Keeps the actual order targets were seen.
        self._seen_set = set()
        self._center_on_targets = True
        self._stop = True
        self._events = []
        self.results = {}
    
    def stopped(self):
        return self._stop
    
    def _unregisterEvents(self):
        # should be idempotent
        for event, callback in self._events:
            self._eventmanager.unregister(callback, event)

    def stop(self):
        self._unregisterEvents()
        self._stop = True
    
    def search(self, targets, center_on_targets = True):
        self._targets = targets
        self._center_on_targets = center_on_targets
        del self._seen_order[:]
        self._seen_set.clear()
        self._stop = False
        # TODO - complete this mapping, add opponent goal, my goal
        
        self.results.clear()
        for target in targets:
            self.results[target] = SearchResults()
        
        # register to in frame event for each target object
        del self._events[:]
        for obj in targets:
            event = obj.in_frame_event 
            callback = lambda obj=obj: self.onSeen(obj)
            self._eventmanager.register(callback, event)
            self._events.append((event, callback))
            
        # TODO: Fix YELLOW to use opponent goal
        self._searchlevel = burst.actions.LOOKAROUND_QUICK
        self._actions.lookaround(self._searchlevel).onDone(self.onScanDone)
        
        # create a burst deferred to be called when we found all targets
        self._bd = BurstDeferred(self)
        return self._bd

    def onOneCentered(self):
        target = self._center_target
        if self.verbose:
            print "Searcher: Center: %s results updated" % target._name
        last_time = self.results[target].sighted_time
        self._updateResults(target)
        self.centerOnNext()

    def centerOnNext(self):
        # need to first go to a close place, use angles last seen
        # TODO - use median of last seen angles, would be much closer
        # to reality
        try:
            self._center_target = target = self._center_targets.next()
        except:
            #import pdb; pdb.set_trace()
            self._onFinishedScanning()
            return

        results = self.results[target]
        if self.verbose:
            print "Searcher: moving towards and centering on %s - (%1.2f, %1.2f)" % (
                target._name, results.head_yaw, results.head_pitch)
        bd = self._actions.moveHead(results.head_yaw, results.head_pitch)
        # we update the stored results after the centering is done
        return bd.onDone(lambda: self._actions.tracker.center(target)).onDone(
            self.onOneCentered)

    def onScanDone(self):
        if self._stop: return
        
        # see which targets have been sighted
        if all([result.sighted for result in self.results.values()]):
            # best case - all done
            self._unregisterEvents()
            if self._center_on_targets:
                # center on every target by reverse order of seen
                # TODO - chainDeferred would have been nicer (a list
                # instead of a 'lisp list' to represent the future)
                # but there is a bug with my getDeferred in context of chainDeferreds
                self._center_targets = reversed(self._seen_order)
                self.centerOnNext()
            else:
                self._onFinishedScanning()
        else:
            # TODO - middleground
            if self.verbose:
                print "Searcher: targets {%s} NOT seen, searching again..." % (','.join(obj._name for obj in self._targets))
            self._searchlevel = (self._searchlevel + 1) % burst.actions.LOOKAROUND_MAX
            self._actions.lookaround(self._searchlevel).onDone(self.onScanDone)

    def _onFinishedScanning(self):
        if self.verbose:
            print "Searcher: DONE"
        self.stop()
        self._bd.callOnDone()

    def onSeen(self, target):
        if self._stop: return
        if not target.seen:
            if self.verbose:
                print "Searcher: onSeen but target not seen?"
            return
        # TODO OPTIMIZATION - when last target is seen, cut the search
        self._updateResults(target) # These are not the centered results.
        if target not in self._seen_set:
            if self.verbose:
                print "Searcher: First Sighting: %s, %s" % (target._name, self.results[target])
            self._seen_order.append(target)
            self._seen_set.add(target)

    def _updateResults(self, target):
        """ Update results for a single target. Only stores the
        results for the most centered sighting - this includes
        everything, vision (centerX/centerY), joint angles (headYaw, headPitch),
        and the world location estimates (distance, bearing, elevation)
        """
        # TODO - if we saw everything then stop scan
        # TODO - if we saw something then track it, only then continue scan
        result = self.results[target]

        if result.sighted: # always do first update
            # We keep the most centered head_yaw and head_pitch using smallest norm2.
            abs_cur_x, abs_cur_y = abs(result.normalized2_centerX), abs(result.normalized2_centerY)
            abs_new_x, abs_new_y = abs(target.normalized2_centerX), abs(target.normalized2_centerY)
            new_dist = abs_new_x**2 + abs_new_y**2
            old_dist = abs_cur_x**2 + abs_cur_y**2
            if new_dist >= old_dist:
                return # no update

        if self.verbose:
            print "Searcher: updating %s, (%1.2f, %1.2f) -> (%1.2f, %1.2f)" % (
                target._name,
                result.normalized2_centerX or -100.0, result.normalized2_centerY or -100.0,
                target.normalized2_centerX, target.normalized2_centerY)

        if hasattr(target, 'distSmoothed'):
            result.distSmoothed = self._world.ball.distSmoothed
        # relative location from naoman
        result.dist = target.dist # TODO - dist->distance
        result.bearing = target.bearing
        result.elevation = target.elevation
        result.head_yaw = self._world.getAngle('HeadYaw')
        result.head_pitch = self._world.getAngle('HeadPitch')
        # vision vars from naoman
        result.height = target.height
        result.width = target.width
        result.centerX = target.centerX
        result.centerY = target.centerY
        result.normalized2_centerX = target.normalized2_centerX
        result.normalized2_centerY = target.normalized2_centerY
        result.x = target.x # upper left corner - not valid for Ball
        result.y = target.y #
        # flag the sighted flag
        result.sighted = True
        result.sighted_time = self._world.time
        
