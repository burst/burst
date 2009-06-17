'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import (BurstDeferred, Nameable, calculate_middle, calculate_relative_pos, polar2cart, cart2polar, nicefloats)

# local imports
import burst
from burst.events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN, EVENT_CHANGE_LOCATION_DONE)
import burst.actions
from burst.actions.target_finder import TargetFinder
import burst.moves as moves
import burst.moves.walks as walks
from burst.behavior_params import (KICK_X_OPT, KICK_Y_OPT, KICK_X_MIN, KICK_X_MAX, KICK_Y_MIN, KICK_Y_MAX,
                                   calcBallArea, BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT,
                                   BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL, MOVEMENT_PERCENTAGE)
from burst_consts import (LEFT, RIGHT, DEFAULT_NORMALIZED_CENTERING_Y_ERROR, IMAGE_CENTER_X, IMAGE_CENTER_Y,
    PIX_TO_RAD_X, PIX_TO_RAD_Y, EVENT_MANAGER_DT)
import burst_consts

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

    def __init__(self, eventmanager, actions, target_left_right_posts, align_to_target=True):
        super(BallKicker, self).__init__(None)
        self._align_to_target = align_to_target
        self._eventmanager = eventmanager
        self._actions = actions
        self._world = eventmanager._world
        self._ballFinder = TargetFinder(actions=actions, targets=[self._world.ball], start=False)
        self._ballFinder.setOnTargetFoundCB(self._approachBall)
        self._ballFinder.setOnTargetLostCB(self._stopOngoingMovement)
        self._goalFinder = TargetFinder(actions=actions, targets=target_left_right_posts, start=False)
        self._goalFinder.setOnTargetFoundCB(self.onGoalFound)

        self._is_strafing = False
        self._is_strafing_init_done = False

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
    # _approachBall helpers (XXX - should they be submethods of _approachBall? would
    # make it cleared to understand the relationship, not require this comment)
    ################################################################################

    def _approachBall(self):
        target = self._world.ball
        
        print "\nApproaching %s: (recently seen %s, dist: %3.3f, distSmoothed: %3.3f, bearing: %3.3f)" % (
                  target.name, target.recently_seen, target.dist, target.distSmoothed, target.bearing)
        print "-"*100

        (target_x, target_y) = polar2cart(target.distSmoothed, target.bearing)
        print "target_x: %3.3fcm, target_y: %3.3fcm" % (target_x, target_y)

        # determine kicking leg
        side = target.bearing < 0 # 0 = LEFT, 1 = RIGHT
        self.debugPrint("Designated kick leg: %s" % (side==LEFT and "LEFT" or "RIGHT"))
        
        # calculate optimal kicking point
        (kp_x, kp_y) = (target_x - KICK_X_OPT[side], target_y - KICK_Y_OPT[side])
        (kp_dist, kp_bearing) = cart2polar(kp_x, kp_y)
        self.debugPrint("kp_x: %3.3fcm   kp_y: %3.3fcm" % (kp_x, kp_y))
        self.debugPrint("kp_dist: %3.3fcm   kp_bearing: %3.3f" % (kp_dist, kp_bearing))

        # ball location, as defined at behavior parameters (front, side, etc...)
        target_location = calcBallArea(target_x, target_y, side)

        # by Vova - new kick TODO: use consts, add explanation of meaning, perhaps move inside adjusted_straight_kick (passing ball, of course)
        kick_side_offset = 1.1-1.2*(abs(target_y-KICK_Y_MIN[side])/7)

        print ('TARGET_IN_KICKING_AREA', 'TARGET_BETWEEN_LEGS', 'TARGET_FRONT', 'TARGET_SIDE_NEAR', 'TARGET_SIDE_FAR', 'TARGET_DIAGONAL')[target_location]

        # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
        if target_location in (BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS) and not self.aligned_to_goal and self._align_to_target:
            self.debugPrint("Aligning to goal! (stopping target tracker)")
            self.switchToFinder(to_goal_finder=True)
        # Ball inside kicking area, kick it
        elif target_location == BALL_IN_KICKING_AREA:
            self.debugPrint("Kicking!")
            if self.ENABLE_MOVEMENT:
                self._ballFinder.stop()
                self._goalFinder.stop()
                self.debugPrint("kick_side_offset: %3.3f" % (kick_side_offset))
                self._actions.setCameraFrameRate(10)
                #self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT, side).onDone(self.callOnDone)
                self._actions.adjusted_straight_kick(side, kick_side_offset).onDone(self.callOnDone)
        else:
            if target_location == BALL_FRONT:
                self.debugPrint("Walking straight!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._nextMovement(self._actions.changeLocationRelative(
                            kp_x*MOVEMENT_PERCENTAGE)).onDone(self._approachBall)
            elif target_location in (BALL_BETWEEN_LEGS, BALL_SIDE_NEAR):
                self.debugPrint("Side-stepping!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._nextMovement(self._actions.changeLocationRelativeSideways(
                        0.0, kp_y*MOVEMENT_PERCENTAGE, walk=walks.SIDESTEP_WALK)).onDone(self._approachBall)
            elif target_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
                self.debugPrint("Turning!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._nextMovement(self._actions.turn(kp_bearing*MOVEMENT_PERCENTAGE)).onDone(self._approachBall)
            else:
                self.debugPrint("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")

        if not self.ENABLE_MOVEMENT:
            self._actions.changeLocationRelative(0, 0, 0).onDone(self._approachBall)

    def switchToFinder(self, to_goal_finder=False):
        from_finder, to_finder = self._goalFinder, self._ballFinder
        if to_goal_finder:
            from_finder, to_finder = self._ballFinder, self._goalFinder
        else:
            # switch to bottom camera when we look for the ball
            # --- DONT DO THIS UNTIL IMOPS CODE DOES THE SWITCHING, or segfault for you ---
            #self._actions.setCamera(burst_consts.CAMERA_WHICH_BOTTOM_CAMERA)
            pass
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
        self._is_strafing = True
        
        if not self.goalpost_to_track.seen:
            self.debugPrint("strafe: goal post not seen")
            # Eran: Needed? won't goal-post searcher wake us up? Can't this create a case where strafe is called twice?
            self._eventmanager.callLater(EVENT_MANAGER_DT, self.strafe)
            return
        self.debugPrint("strafe: goal post seen")
        # TODO: Add align-to-goal-center support
        if self.goalpost_to_track.bearing < -DEFAULT_NORMALIZED_CENTERING_Y_ERROR:
            strafeMove = self._actions.executeCircleStrafeClockwise
        elif self.goalpost_to_track.bearing > DEFAULT_NORMALIZED_CENTERING_Y_ERROR:
            strafeMove = self._actions.executeCircleStrafeCounterClockwise
        else:
            self._is_strafing = False
            self._is_strafing_init_done = False
            self.debugPrint("Aligned position reached! (starting ball search)")
            self.aligned_to_goal = True
            self._actions.setCameraFrameRate(20)
            self._goalFinder.stop()
            self.refindBall()
            return
        
        # do strafing move
        self._actions.setCameraFrameRate(10)

        if not self._is_strafing_init_done:
            self.debugPrint("Aligning and strafing...")
            self._is_strafing_init_done = True
            bd = self._actions.executeCircleStraferInitPose()
            bd.onDone(lambda: self._nextMovement(strafeMove()))
        else:
            self.debugPrint("Strafing...")
            bd = strafeMove()
        
        self._nextMovement(bd).onDone(self.strafe)

    def refindBall(self):
        self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_BOTTOM).onDone(
            # TODO: Fix distSmooth after moving head - this is just a workaround
            lambda: self._eventmanager.callLater(0.5,
                 lambda: self.switchToFinder(to_goal_finder=False))
        )
