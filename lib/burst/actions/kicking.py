'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import (BurstDeferred, Nameable, calculate_middle, calculate_relative_pos, polar2cart, cart2polar, nicefloats)

# local imports
import burst
from burst.events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN, EVENT_CHANGE_LOCATION_DONE)
import burst.actions
import burst.moves as moves
from burst.behavior_params import (KICK_X_OPT, KICK_Y_OPT, KICK_X_MIN, KICK_X_MAX, KICK_Y_MIN, KICK_Y_MAX,
                                   calcBallArea, BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT,
                                   BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL, MOVEMENT_PERCENTAGE)
from burst_consts import LEFT, RIGHT, DEFAULT_NORMALIZED_CENTERING_Y_ERROR, IMAGE_CENTER_X, IMAGE_CENTER_Y, PIX_TO_RAD_X, PIX_TO_RAD_Y
from burst.behavior import ContinuousBehavior, Behavior

class TargetFinder(ContinuousBehavior):
    ''' Continuous target finder & tracker '''

    def __init__(self, actions, targets, start = True):
        super(TargetFinder, self).__init__(actions=actions, name='%s Finder' % [
                                    target.name for target in targets])
        if len(targets) < 1:
            raise RuntimeException("Cannot find null set")
        self._targets = targets
        self._onTargetFoundCB = None
        self._onTargetLostCB = None
        self.verbose = False
        if start:
            self.start()

    def setOnTargetFoundCB(self, cb):
        self._onTargetFoundCB = cb

    def _callOnTargetFoundCB(self):
        if self._onTargetFoundCB:
            self._onTargetFoundCB()

    def setOnTargetLostCB(self, cb):
        self._onTargetLostCB = cb

    def _callOnTargetLostCB(self):
        if self._onTargetLostCB:
            self._onTargetLostCB()

    def getTargets(self):
        return self._targets

    def _start(self):
        print "Starting TargetFinder, targets = %s" % (','.join(s.name for s in self._targets))
        # if target location is not known, search for it
        
        # If a search has completed with our targets and they were found in this frame, go to tracking.
        seen_objects = [t for t in self._targets if t.seen]

        if len(seen_objects) > 0:
            # reset targets to the first seen object (could be arbitrary if we were just called)
            self._targets =  [seen_objects[0]]
            target = self._targets[0]
            self.printDebug("will track %s" % target.name)
            # NOTE: to make the behavior happy we need to always keep the deferred we are
            # waiting on at self._bd ; because Tracker doesn't provide any bd we create
            # one using self._actions._make
            self._bd = self._actions._make(self)
            self._bd.onDone(self._start)
            self._actions.track(target, lostCallback=self._bd.callOnDone)
            self._callOnTargetFoundCB()
        else:
            # none of our targets are currently seen, start a new search.
            self.printDebug("targets not seen (%s), searching for it" % [t.name for t in self._targets])
            self._bd = self._actions.search(self._targets, center_on_targets=True)
            self._bd.onDone(self._start)
            self._callOnTargetLostCB()

    def stop(self):
        super(TargetFinder, self).stop()
        self._actions.tracker.stop()
        self._actions.searcher.stop()

class TargetApproacher(TargetFinder):
    pass
    

#===============================================================================
#    Logic for Kicking behavior:
#
# 1. Scan for ball
# 2. Advance towards ball (while tracking ball)
# 3. When near ball, circle-strafe (to correct direction) till goal is seen and centered (goal is tracked)
# 4. Search ball down, align against ball and kick
#
# Handling ball lost:
# 1. While walking towards it => notify caller (kind of restart behavior)
# 2. While aligning for kick => search front (if found - align and kick, if not -> notify caller)
# 3. If full scan doesn't find ball => notify caller
#
# *TODO*:
# * RESET self.aligned_to_goal when needed
# * Area for strafing different from kicking-area
# * Handle "ball lost" only when ball isn't seen for several frames (use the "recently seen" variable)
# * Notify caller when ball moves (yet doesn't disappear)? Since measurements are noisy, need to decide
#    how to determine when ball moved.
# * Need to handle negative target location? (walk backwards instead of really big turns...)
# * SEARCH: If ball location isn't known and yet ball was seen recently, center on ball (to get better distance, then continue)
# * SEARCH: Searching should also move the body, not just the head
# * Obstacle avoidance
#===============================================================================

class BallKicker(BurstDeferred):

    VERBOSE = True
    ENABLE_MOVEMENT = True

    def __init__(self, eventmanager, actions, align_to_target=True):
        super(BallKicker, self).__init__(None)
        self._align_to_target = align_to_target
        self._eventmanager = eventmanager
        self._actions = actions
        self._world = eventmanager._world
        self._ballFinder = TargetFinder(actions=actions, targets=[self._world.ball], start=False)
        self._ballFinder.setOnTargetFoundCB(self.doNextAction)
        self._ballFinder.setOnTargetLostCB(self._stopOngoingMovement)
        self._goalFinder = TargetFinder(actions=actions, targets=[self._world.yglp, self._world.ygrp], start=False)
        self._goalFinder.setOnTargetFoundCB(self.onGoalFound)

        self._is_strafing = False

        # Strafing differs between webots since webots cannot do the CW/CCW
        # turns, so we emulate it with a turn in place.
        if burst.connecting_to_webots():
            self.strafe_cw = lambda: self._actions.turn(-0.2)
            self.strafe_ccw = lambda: self._actions.turn(0.2)
        else:
            self.strafe_cw = self._actions.executeTurnCW
            self.strafe_ccw = self._actions.executeTurnCCW

    ################################################################################

    def debugPrint(self, message):
        if self.VERBOSE:
            print "Kicking:", message

    def _nextMovement(self, bd):
        """ store current movement deferred for clearing if we need to stop movement
        """
        self._movement_deferred = bd
        return bd

    ################################################################################

    def start(self):
        self.aligned_to_goal = False
        self.goalposts = [self._world.yglp, self._world.ygrp]
        self.movement_deferred = None

        self._actions.setCameraFrameRate(20)
        # kicker initial position
        self._actions.executeMoveRadians(moves.STRAIGHT_WALK_INITIAL_POSE).onDone(
            lambda: self.switchToFinder(to_goal_finder=False))

    def _stopOngoingMovement(self):
        if self.movement_deferred:
            self._actions.clearFootsteps() # TODO - flag something? someone?
            self.movement_deferred.clear()

    ################################################################################
    # doNextAction helpers (XXX - should they be submethods of doNextAction? would
    # make it cleared to understand the relationship, not require this comment)
    ################################################################################

    def doNextAction(self):
        print "\nDeciding on next move: (ball recently seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (
            self._world.ball.recently_seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        print "-"*100

        # for now, just directly approach ball and kick it wherever
        ballBearing = self._world.ball.bearing
        ballDist = self._world.ball.distSmoothed
        (ball_x, ball_y) = polar2cart(ballDist, ballBearing)
        print "ball_x: %3.3fcm, ball_y: %3.3fcm" % (ball_x, ball_y)

        # determine kicking leg
        side = ballBearing < 0 # 0 = LEFT, 1 = RIGHT
        if (side == LEFT): self.debugPrint("Designated kick leg: Left")
        else: self.debugPrint("Designated kick leg: Right")

        # calculate optimal kicking point
        (kp_x, kp_y) = (ball_x - KICK_X_OPT[side], ball_y - KICK_Y_OPT[side])
        (kp_dist, kp_bearing) = cart2polar(kp_x, kp_y)
        self.debugPrint("kp_x: %3.3fcm   kp_y: %3.3fcm" % (kp_x, kp_y))
        self.debugPrint("kp_dist: %3.3fcm   kp_bearing: %3.3f" % (kp_dist, kp_bearing))

        # ball location, as defined at behavior parameters (front, side, etc...)
        ball_location = calcBallArea(ball_x, ball_y, side)

        # by Vova - new kick TODO: use consts, add explanation of meaning, perhaps move inside adjusted_straight_kick (passing ball, of course)
        if side==LEFT:
            cntr_param = 1.1-1.2*(ball_y-KICK_Y_MIN[LEFT])/7
        else:
            cntr_param = 1.1- 1.2*(abs(ball_y-KICK_Y_MIN[RIGHT])/7)

        print ('BALL_IN_KICKING_AREA', 'BALL_BETWEEN_LEGS', 'BALL_FRONT', 'BALL_SIDE_NEAR', 'BALL_SIDE_FAR', 'BALL_DIAGONAL')[ball_location]

        # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
        if ball_location in (BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS) and not self.aligned_to_goal and self._align_to_target:
            self.debugPrint("Aligning to goal! (stopping ball tracker)")
            self.switchToFinder(to_goal_finder=True)
        # Ball inside kicking area, kick it
        elif ball_location == BALL_IN_KICKING_AREA:
            self.debugPrint("Kicking!")
            if self.ENABLE_MOVEMENT:
                self._ballFinder.stop()
                self._goalFinder.stop()
                # by Vova - new kick
                #self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT, side).onDone(self.callOnDone)
                self.debugPrint("cntr_param: %3.3f" % (cntr_param))
                self._actions.setCameraFrameRate(10)
                self._actions.adjusted_straight_kick(side, cntr_param).onDone(self.callOnDone)
        else:
            if ball_location == BALL_FRONT:
                self.debugPrint("Walking straight!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._nextMovement(self._actions.changeLocationRelative(
                            kp_x*MOVEMENT_PERCENTAGE)).onDone(self.doNextAction)
            elif ball_location in (BALL_BETWEEN_LEGS, BALL_SIDE_NEAR):
                self.debugPrint("Side-stepping!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._nextMovement(self._actions.changeLocationRelativeSideways(
                        0.0, kp_y*MOVEMENT_PERCENTAGE, walk=moves.SIDESTEP_WALK)).onDone(self.doNextAction)
            elif ball_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
                self.debugPrint("Turning!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._nextMovement(self._actions.turn(kp_bearing*MOVEMENT_PERCENTAGE)).onDone(self.doNextAction)
            else:
                self.debugPrint("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")

        if not self.ENABLE_MOVEMENT:
            self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)

    def switchToFinder(self, to_goal_finder=False):
        from_finder, to_finder = self._goalFinder, self._ballFinder
        if to_goal_finder:
            from_finder, to_finder = self._ballFinder, self._goalFinder
        if not from_finder.stopped():
            print "STOPPING %s" % from_finder.name
            from_finder.stop()
        print "SwitchToFinder: calling %s.start" % (to_finder.name)
        if to_finder.stopped(): to_finder.start()

    ################################################################################
    # Strafing

    def onGoalFound(self):
        self.debugPrint('onGoalFound')
        if not self._is_strafing:
            self.goalpost_to_track = self._goalFinder.getTargets()[0]
            g = self.goalpost_to_track
            self.debugPrint('onGoalFound: found %s at %s, %s (%s)' % (g.name,
                g.centerX, g.centerY, g.seen)) 
            self.strafe()

    def strafe(self):
        if not self.goalpost_to_track.recently_seen:
            self.debugPrint("strafe: goal post not seen")
            return
        self.debugPrint("strafe: goal location recently seen")
        # TODO: Add align-to-goal-center support
        if self.goalpost_to_track.bearing < -DEFAULT_NORMALIZED_CENTERING_Y_ERROR:
            strafe = self.strafe_cw
        elif self.goalpost_to_track.bearing > DEFAULT_NORMALIZED_CENTERING_Y_ERROR:
            strafe = self.strafe_ccw
        else:
            self._is_strafing = False
            self.debugPrint("Aligned position reached! (starting ball search)")
            self.aligned_to_goal = True
            self._actions.setCameraFrameRate(20)
            self._goalFinder.stop()
            self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_BOTTOM).onDone(
                lambda: self.switchToFinder(to_goal_finder=False))
            return
        # start strafing
        self._is_strafing = True
        self._actions.setCameraFrameRate(10)
        self._nextMovement(strafe()).onDone(self.strafe)
