'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import (BurstDeferred, Nameable, calculate_middle, calculate_relative_pos, polar2cart, cart2polar, nicefloats)

# local imports
import burst
from burst.events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN, EVENT_CHANGE_LOCATION_DONE,
                          EVENT_OBSTACLE_SEEN, EVENT_OBSTACLE_LOST, EVENT_OBSTACLE_IN_FRAME)
import burst.actions
from burst.actions.target_finder import TargetFinder
import burst.moves as moves
import burst.moves.walks as walks
import burst.moves.poses as poses

from burst.behavior_params import (calcTarget, BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT_NEAR, 
                                   BALL_FRONT_FAR, BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL, MOVEMENT_PERCENTAGE,
                                   MOVE_FORWARD, MOVE_ARC, MOVE_TURN, MOVE_SIDEWAYS, MOVE_CIRCLE_STRAFE, MOVE_KICK)
from burst_consts import (LEFT, RIGHT, DEFAULT_NORMALIZED_CENTERING_Y_ERROR, IMAGE_CENTER_X, IMAGE_CENTER_Y,
    PIX_TO_RAD_X, PIX_TO_RAD_Y, DEG_TO_RAD)
import burst_consts
import random

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
# * RESET self._aligned_to_goal when needed
# * Handle "ball lost" only when ball isn't seen for several frames (use the "recently seen" variable)
# * Notify caller when ball moves (yet doesn't disappear)? Since measurements are noisy, need to decide
#   how to determine when ball moved.
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

        self._ultrasound = self._world.robot.ultrasound
        self._eventmanager.register(self.onObstacleSeen, EVENT_OBSTACLE_SEEN)
        self._eventmanager.register(self.onObstacleLost, EVENT_OBSTACLE_LOST)
        self._eventmanager.register(self.onObstacleInFrame, EVENT_OBSTACLE_IN_FRAME) 
        
        self._ballFinder = TargetFinder(actions=actions, targets=[self._world.ball], start=False)
        self._ballFinder.setOnTargetFoundCB(self._approachBall)
        self._ballFinder.setOnTargetLostCB(self._stopOngoingMovement)
        self._goalFinder = TargetFinder(actions=actions, targets=target_left_right_posts, start=False)
        self._goalFinder.setOnTargetFoundCB(self.onGoalFound)

    def start(self):
        self._aligned_to_goal = False
        self._movement_deferred = None
        self._movement_type = None
        self._movement_location = None
        
        self._is_strafing = False
        self._is_strafing_init_done = False

        self._obstacle_in_front = None        
        self._target = self._world.ball

        self._actions.setCameraFrameRate(20)
        # kicker initial position
        self._actions.executeMoveRadians(poses.STRAIGHT_WALK_INITIAL_POSE).onDone(
            lambda: self.switchToFinder(to_goal_finder=False))

    ################################################################################
    # Handling movements
    #
    def _clearMovement(self, clearFootsteps = False):
        if self._movement_deferred:
            self._movement_deferred.clear()
            if clearFootsteps and self._movement_type in (MOVE_FORWARD, MOVE_SIDEWAYS, MOVE_TURN, MOVE_ARC):
                print "CLEARING FOOTSTEPS!"
                self._actions.clearFootsteps()
        self._movement_deferred = None
        self._movement_type = None
        self._movement_location = None

    def _onMovementFinished(self, nextAction):
        print "Movement DONE!"
        self._clearMovement(clearFootsteps = False)
        nextAction()

    def _stopOngoingMovement(self, forceStop = False):
        # stop movement if we're forced or if it's a long walk-forward move
        shouldStopMovement = forceStop or (self._movement_type == MOVE_FORWARD and self._movement_location == BALL_FRONT_FAR)
        if shouldStopMovement:
            self._clearMovement(clearFootsteps = True)
        
        print "Kicking: _stopOngoingMovement: current movement %s (forceStop = %s)" % (shouldStopMovement and "STOPPED" or "CONTINUES", forceStop)
        
    ################################################################################
    # Ultrasound callbacks
    #
    def onObstacleSeen(self):
        obstacle = self._ultrasound.getLastReading()
        print "Obstacle seen (on %s, distance of %f)!" % (obstacle)

        if self._movement_deferred:
            print "NOTE: Obstacle in front while a movement is in progress"
            # if walking forward and ball is far, stop
            if self._movement_type == MOVE_FORWARD and self._movement_location == BALL_FRONT_FAR:
                self._stopOngoingMovement(forceStop = True)
                self._eventmanager.callLater(0.5, self._approachBall)

    def onObstacleLost(self):
        print "Obstacle lost!"

    def onObstacleInFrame(self):
        #print "Obstacle in frame!"
        pass

    ################################################################################
    # _approachBall helpers (XXX - should they be submethods of _approachBall? would
    # make it cleared to understand the relationship, not require this comment)
    #
    def _approachBall(self):
        print ("\nApproaching %s: (recently seen %s, dist: %3.3f, distSmoothed: %3.3f, bearing: %3.3f)"+"\n"+"-"*100) % (
                  self._target.name, self._target.recently_seen, self._target.dist, self._target.distSmoothed, self._target.bearing)

        # TODO: we probably need a better solution? this can happen after we're aligned,
        # when ball tracker finds the ball while a previous movement is still ON.
        if self._movement_deferred:
            print "LAST MOVEMENT STILL ON!!!"
            #import pdb; pdb.set_trace()
            return

        if not self._target.recently_seen:
            print "TARGET NOT RECENTLY SEEN???"
            #import pdb; pdb.set_trace()
            return
        
        (side, kp_x, kp_y, kp_dist, kp_bearing, target_location, kick_side_offset) = calcTarget(self._target.distSmoothed, self._target.bearing)

        ### DECIDE ON NEXT MOVEMENT ###
        # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
        if target_location in (BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT_NEAR) and not self._aligned_to_goal and self._align_to_target:
            self.debugPrint("Aligning to goal! (stopping target tracker)")
            self._actions.setCameraFrameRate(20)
            self.switchToFinder(to_goal_finder=True)
            return
        # Ball inside kicking area, kick it
        elif target_location == BALL_IN_KICKING_AREA:
            self.debugPrint("Kicking!")
            if self.ENABLE_MOVEMENT:
                self._ballFinder.stop()
                self._goalFinder.stop()
                self.debugPrint("kick_side_offset: %3.3f" % (kick_side_offset))
                self._actions.setCameraFrameRate(10)
                #self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT, side).onDone(self.callOnDone)
                self._movement_type = MOVE_KICK
                self._movement_location = target_location
                self._movement_deferred = self._actions.adjusted_straight_kick(side, kick_side_offset)
                self._movement_deferred.onDone(self.callOnDone)
                return
        else:
            if target_location in (BALL_FRONT_NEAR, BALL_FRONT_FAR):
                self.debugPrint("Walking straight!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._movement_type = MOVE_FORWARD
                    self._movement_location = target_location
                    self._movement_deferred = self._actions.changeLocationRelative(kp_x*MOVEMENT_PERCENTAGE)
            elif target_location in (BALL_BETWEEN_LEGS, BALL_SIDE_NEAR):
                self.debugPrint("Side-stepping!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    self._movement_type = MOVE_SIDEWAYS
                    self._movement_location = target_location
                    self._movement_deferred = self._actions.changeLocationRelativeSideways(
                        0.0, kp_y*MOVEMENT_PERCENTAGE, walk=walks.SIDESTEP_WALK)
            elif target_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
                self.debugPrint("Turning!")
                if self.ENABLE_MOVEMENT:
                    self._actions.setCameraFrameRate(10)
                    # if we do a significant turn, our goal-alignment isn't worth much anymore...
                    if kp_bearing > 10*DEG_TO_RAD:
                        self._aligned_to_goal = False
                    self._movement_type = MOVE_TURN
                    self._movement_location = target_location
                    self._movement_deferred = self._actions.turn(kp_bearing*MOVEMENT_PERCENTAGE)
            else:
                self.debugPrint("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")
                #import pdb; pdb.set_trace()

        if not self.ENABLE_MOVEMENT:
            self._movement_type = MOVE_FORWARD
            self._movement_location = target_location
            self._movement_deferred = self._actions.changeLocationRelative(0, 0, 0)
        
        print "Movement STARTING!"
        self._movement_deferred.onDone(lambda _, nextAction=self._approachBall: self._onMovementFinished(nextAction))
        
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
            self._eventmanager.callLater(self._eventmanager.dt, self.strafe)
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
            self._aligned_to_goal = True
            self._actions.setCameraFrameRate(20)
            self._goalFinder.stop()
            self.refindBall()
            return

        # TODO: FPS=10 removed for now (for accurate feedback), might be needed for stable circle-strafing!
        #self._actions.setCameraFrameRate(10)

        self._movement_type = MOVE_CIRCLE_STRAFE
        self._movement_location = BALL_BETWEEN_LEGS
        if not self._is_strafing_init_done:
            self.debugPrint("Aligning and strafing...")
            self._is_strafing_init_done = True
            self._movement_deferred = self._actions.executeCircleStraferInitPose().onDone(strafeMove)
        else:
            self.debugPrint("Strafing...")
            self._movement_deferred = strafeMove()

        # We use call later to allow the strafing to handle the correct image (otherwise we get too much strafing)
        nextAction = lambda _: self._onMovementFinished(lambda: self._eventmanager.callLater(0.2, self.strafe))
        
        print "Movement STARTING! (strafing)"
        self._movement_deferred.onDone(nextAction)
        

    def refindBall(self):
        self._actions.executeHeadMove(poses.HEAD_MOVE_FRONT_BOTTOM).onDone(
            # TODO: Fix distSmooth after moving head - this is just a workaround
            lambda: self._eventmanager.callLater(0.5,
                 lambda: self.switchToFinder(to_goal_finder=False)))

    def debugPrint(self, message):
        if self.VERBOSE:
            print "Kicking:", message
