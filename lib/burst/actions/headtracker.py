import sys
import linecache
from math import pi, sqrt

from burst_util import (traceme, nicefloat, BurstDeferred,
    Deferred, chainDeferreds, func_name, trackedlist)
from burst_events import *
import burst
import burst_consts as consts
from burst_consts import (FOV_X, FOV_Y,
    DEFAULT_NORMALIZED_CENTERING_X_ERROR,
    DEFAULT_NORMALIZED_CENTERING_Y_ERROR, PIX_TO_RAD_X, PIX_TO_RAD_Y,
    IMAGE_CENTER_X, IMAGE_CENTER_Y)
import burst_events
from burst.image import normalized2_image_width, normalized2_image_height
from burst.behavior import Behavior, ContinuousBehavior

def donothing():
    pass

class TrackMixin(object):
    """ used by Centerer and Tracker for common functions. A Mixin - doesn't
    have an __init__ method. This mixin is only for Behaviors or anything
    with a self._actions and self.log """

    _centering_normalized_x_error = 0.1 # TODO - this should depend on distance?
    _centering_normalized_y_error = 0.1

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
        head_motion_in_progress = self._actions.isHeadMotionInProgress()
        if target.seen and not centered and not head_motion_in_progress:
            CAM_X_TO_RAD_FACTOR = (FOV_X / 2)/2 # do half the error in a single step
            CAM_Y_TO_RAD_FACTOR = (FOV_Y / 2)/2
            deltaHeadYaw   = -xNormalized * CAM_X_TO_RAD_FACTOR #* (0.5 + (1-sqrt(abs(xNormalized)))/2) # move less for far-away targets, wise?
            deltaHeadPitch =  yNormalized * CAM_Y_TO_RAD_FACTOR #* (0.5 + (1-sqrt(abs(yNormalized)))/2) # move less for far-away targets, wise?
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
            self.log("Tracker calculation: %s, %s, %s, center %3.1f, %3.1f, error (%1.2f, %1.2f)%s" % (
                centered, centered_at_pitch_limit,
                head_motion_in_progress and 'head moving' or 'head ready',
                target.centerX, target.centerY, xNormalized, yNormalized, angles))
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
            bd = self._actions.changeHeadAnglesRelative(*delta_angles) #changeHeadAnglesRelative / changeHeadAnglesRelativeChained
        if return_exact_error:
            return centered, bd, error
        return centered, bd

############################################################################

CENTERING_GIVE_UP_TIME = 5.0

class Centerer(Behavior, TrackMixin):

    """ center on target by moving the head """

    movehead = False

    def __init__(self, actions):
        super(Centerer, self).__init__(actions=actions, name="Centerer")
        self._ondone = trackedlist()
        self._target = None
        self._on_lost_callback = donothing
        self._on_timeout_callback = donothing
        self.verbose = burst.options.verbose_tracker # turn on for debugging
        self.debug = self.verbose and burst.options.debug

        # DEBUG
        #self._trackingStep = traceme(self._trackingStep)

    def _start(self, firstTime, target, lostCallback=donothing, timeout=None, timeoutCallback=donothing):
        """
        Center on target, returns a BurstDeferred.
        """
        # TODO - automate this via locking. NOTE: It is ok for the Searcher to do Centering (it does that shit).
        if not self._actions.tracker.stopped:
            self.log("ERROR: Center while Track")
            import pdb; pdb.set_trace()
        self._target = target
        self._on_lost_callback = lostCallback
        # TODO - what happens if the target is lost during the centering,
        #  but it doesn't have an associated "lost" event? lost can
        # happen because of occlusion, and because of vision problems (which
        # can be minimized maybe).

        #if not target.recently_seen: # don't start centering on a target that isn't visible
        #    print "ERROR: center called when target not recently in sight"
        #    return
        if self.verbose:
            self.log("Start Centering on %s" % target.name)
        # TODO MAJORLY: This fixes the bug, but real fix is in BurstDeferred
        self._eventmanager.callLater(self._eventmanager.dt, self._centeringStep)
        self._timeout = timeout
        self._on_timeout_callback = timeoutCallback
        if timeout is not None:
            self._eventmanager.callLater(timeout, self._centeringOnTimeout)
        #self._centeringStep()
        # centering step we are already centered (by calling center twice!)

    def _stop(self):
        if self.verbose:
            self.log("Stopping current action")
        self._on_lost_callback = donothing
        self._on_timeout_callback = None
        self._timeout = None
        # clear ourselves from the current bd.
        return self._actions.getCurrentHeadBD()

    def _centeringOnTimeout(self):
        if self.verbose:
            print "Tracking: Centering: Timeout (%s)" % (self._timeout)
        self.stop().onDone(self._on_timeout_callback)

    def _centeringStep(self):
        if self.stopped: return
        # TODO - this should be done through a registration mechanism in World, like the default objects.
        #if hasattr(self.target, 'update'):
        #    self.target.update()
        dt = self._world.time - self._target.update_time
        self.logverbose("%3.2f since target seen, %s" % (dt, self._target))
        if not self._target.recently_seen and dt > CENTERING_GIVE_UP_TIME:
            self.logverbose("CenteringStep: %s not seen for %s, calling _on_lost_callback" % (self._target.name, CENTERING_GIVE_UP_TIME))
            return self.stop().onDone(self._on_lost_callback)
        centered, centered_at_pitch_limit, delta_angles, error = self.calculateTracking(self._target,
            normalized_error_x=self._centering_normalized_x_error,
            normalized_error_y=self._centering_normalized_y_error)
        self.logverbose("CenteringStep: centered = %s, delta_angles %s, centered_at_pitch_limit = %s" % (centered,
                delta_angles or 'is None', centered_at_pitch_limit))
        if centered or centered_at_pitch_limit:
            self.logverbose("CenteringStep: DONE")
            return self.stop()
        if delta_angles:
            self.logverbose("Out #1: Delta Angles")
            # Out path 1: wait for change angles relative to complete
            self._actions.changeHeadAnglesRelative(*delta_angles).onDone(self._centeringStep)
        else: # target.recently_seen is True
            # Out path 2: try to move to the pitch limit (we lost it, let's try finding it the cheap way)
            if self.movehead:
                self.logverbose("Out #2-move: Moving head up")
                self._actions.changeHeadAnglesRelative(0.0, -0.1).onDone(self._centeringStep)
            else:
                # old path 2: wait a little
                #self.log("Out #2-wait: Waiting one frame")
                self._eventmanager.callLater(self._eventmanager.dt, self._centeringStep)

############################################################################

class GoalPostCenterer(object):

    # TODO: What if all goalposts are suddenly lost?

    MAXMINAL_PIXEL_DISTANCE = 20 # TODO: Relative to the size of the image.

    def __init__(self, world, actions, obj, cb):
        self.world = world
        self.actions = actions
        self.obj = obj
        self.cb = cb
        self.start()

    def start(self):
        self.loop(firstTime=True)

    def loop(self, _=None, firstTime=False):
        print "loop"
        # Determine which goalpost you're centering on (since unknown might sometimes change into rp/lp, and vice versa)
        if firstTime:
            goalpost = self.obj
        else:
            if self.obj in self.world.our_goal.left_right_unknown:
                trio = self.world.our_goal.left_right_unknown
            else:
                trio = self.world.opposing_goal.left_right_unknown
            trio = filter(lambda x: x.seen, trio)
            print "!", trio
            goalpost = None
            for potential_goalpost in filter(lambda x: x.seen, trio):
                if goalpost == None or (abs(goalpost.centerX - consts.IMAGE_CENTER_X) > 
                        abs(potential_goalpost.centerX - consts.IMAGE_CENTER_X)):
                    goalpost = potential_goalpost
        if goalpost is None:
            print "GoalPostCenterer on empty"
            # didn't find *any* goal post - sleep (will have a stop flag on this function)
            self.actions._eventmanager.callLater(0.1, self.loop)
            return
        # If you're close enough to that goalpost, you're done:
        if abs(consts.IMAGE_CENTER_X - goalpost.centerX) <= GoalPostCenterer.MAXMINAL_PIXEL_DISTANCE:
            self.stop(goalpost)
        # Otherwise, move closer to that goalpost:
        else:
            delta = ((consts.IMAGE_CENTER_X - goalpost.centerX) / consts.IMAGE_WIDTH) * (FOV_X/4.0)
            print "delta:", delta
            self.actions.changeHeadAnglesRelative(delta, 0.0).onDone(self.loop)

    def stop(self, goalpost):
        self.cb(goalpost)

############################################################################

class Tracker(ContinuousBehavior, TrackMixin):

    """ track a target by moving the head """

    def __init__(self, actions):
        super(ContinuousBehavior, self).__init__(actions=actions, name='Tracker')
        self._target = None
        self._on_lost_callback = donothing

        self.verbose = burst.options.verbose_tracker # turn on for debugging
        self.debug = self.verbose and burst.options.debug
        # DEBUG
        #self._trackingStep = traceme(self._trackingStep)

    def _start(self, firstTime, target, lostCallback=donothing):
        """ Continuous tracking: keep the target in sight.
        """
        self._target = target
        self._on_lost_callback = lostCallback
        # Check for conflicting actions
        # TODO - automate this via locking.
        if not self._actions.searcher.stopped or not self._actions.centerer.stopped:
            self.log("ERROR: Track while %s" % ('Track' if self._actions.searcher.stopped else 'Search'))
            import pdb; pdb.set_trace()

        # don't track objects that are not seen
        if not target.recently_seen:
            # TODO we immediately call the on_lost_callback - might
            # not be wise - could lead to loops
            return self.stop().onDone(lostCallback)
        #self._stepsTillCentered = 0
        self._trackingStep()

    def _stop(self):
        # don't erase any deferreds here! stop is called
        # before issuing the callbacks, allowing deferred's callee to
        # correctly check that tracker is not operating.
        if self.verbose:
            self.log("Stopping current action")
        return self._actions.getCurrentHeadBD()

    def _trackingStep(self):
        # TODO - we check self._target.seen explicitly, not relying on the
        # self.stop() call in self.onLost (tied to the event_lost), because
        # this avoids the case where this callback is called before the event
        # lost one - how to solve this in a nicer manner?
        if self.stopped: return # Stopped
        if not self._target.recently_seen:
            # Target lost
            if self.verbose:
                self.log("TrackingStep: %s not recently seen, calling _on_lost_callback" % self._target.name)
            return self.stop().onDone(self._on_lost_callback)
        centered, maybe_bd = self.executeTracking(self._target)
        #if not centered:
        #    self._stepsTillCentered += 1
        #print "self._stepsTillCentered: %f" % self._stepsTillCentered

        if self.verbose:
            self.log("TrackingStep: centered = %s, maybe_bd %s" % (centered,
                not maybe_bd and 'is None' or 'is a deferred'))
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
                    self.log("TrackingStep: %s not visible right now" % (self._target.name))
            # target is centered or we lost it for a short period (we thing), so just callLater
            #import pdb; pdb.set_trace()
            self._eventmanager.callLater(self._eventmanager.dt, self._trackingStep)

