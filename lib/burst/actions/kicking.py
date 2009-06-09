from burst_util import (BurstDeferred, calculate_middle, calculate_relative_pos, polar2cart, cart2polar, nicefloats)

# local imports
import burst
from burst.events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN, EVENT_CHANGE_LOCATION_DONE)
import burst.actions
import burst.moves as moves
from burst.behavior_params import (KICK_X_OPT, KICK_Y_OPT, KICK_X_MIN, KICK_X_MAX, KICK_Y_MIN, KICK_Y_MAX, 
                                   calcBallArea, BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT, 
                                   BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL, MOVEMENT_PERCENTAGE)
from burst_consts import LEFT, RIGHT, DEFAULT_CENTERING_Y_ERROR, IMAGE_CENTER_X, IMAGE_CENTER_Y, PIX_TO_RAD_X, PIX_TO_RAD_Y

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
    ENABLE_STRAFING = False

    def __init__(self, eventmanager, actions, target_bearing_distance=None):
        super(BallKicker, self).__init__(None)
        if target_bearing_distance is not None:
            raise NotImplemented('BallKicker can only hit the goal right now')
        self._eventmanager = eventmanager
        self._actions = actions
        self._world = eventmanager._world

    def debugPrint(self, message):
        if self.VERBOSE:
            print message
    
    def start(self):
        self.ballLocationKnown = False
        self.goalLocationKnown = False
        self.aligned_to_goal = False
        self.goalpost_to_track = self._world.ygrp
        
        self._actions.initPoseAndStiffness().onDone(self.initKickerPosition)
        
    def initKickerPosition(self):
        self._actions.executeMoveRadians(moves.STRAIGHT_WALK_INITIAL_POSE).onDone(self.doNextAction)
        
    def searchBall(self):
        #self._actions.tracker.stop() # needed???
        self.debugPrint("Starting search")
        self._actions.search([self._world.ball], center_on_targets=False).onDone(self.onSearchBallOver)

    def onSearchBallOver(self):
        # Ball found, track it
        self.debugPrint("onSearchBallOver")
        
        # TODO: TEMP!!! move code elsewhere (should be done in search...)
        self.debugPrint("manually centering on ball (from search ball results)")
        self.manualCentering(self._world.ball.centered_self, self.onSearchCenteringDone)

    def manualCentering(self, centeredTarget, onDoneCallback):
        self.debugPrint("XXX Moving towards and centering on target - (%1.2f, %1.2f, %1.2f, %1.2f)" % (centeredTarget.head_yaw, centeredTarget.head_pitch, centeredTarget.centerX, centeredTarget.centerY))
        a1 = centeredTarget.head_yaw, centeredTarget.head_pitch
        a2 = (a1[0] - PIX_TO_RAD_X * (centeredTarget.centerX - IMAGE_CENTER_X),
              a1[1] + PIX_TO_RAD_Y * (centeredTarget.centerY - IMAGE_CENTER_Y))
        self._actions.moveHead(*a2).onDone(onDoneCallback)
        
    def onSearchCenteringDone(self):
        # TODO: TEMP!!! should be at onSearchBallOver, moved temporarily here since we do the centering by ourself
        self._actions.track(self._world.ball, self.onLostBall)
        self.ballLocationKnown = True
        self.doNextAction()
        
    def onLostBall(self):
        self.debugPrint("BALL LOST, clearing footsteps")
        self._actions.clearFootsteps()
        self.ballLocationKnown = False
        self.doNextAction()

    def doNextAction(self):
        print "\nDeciding on next move: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (
            self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        print "-"*100

        # if kicking-point is not known, search for it
        if not self.ballLocationKnown:
            if self._world.ball.seen:
                self.debugPrint("Ball seen, tracking ball!")
                self.ballLocationKnown = True
                self._actions.track(self._world.ball, self.onLostBall)
            else:
                self.debugPrint("Ball not seen, searching for ball")
                # Search the ball
                self.searchBall()
                return

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
        
        # Use circle-strafing when near ball
        if ball_location in (BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS) and not self.aligned_to_goal and self.ENABLE_STRAFING:
            self.debugPrint("Aligning to goal! (stopping ball tracker)")
            self._actions.tracker.stop()
            # TODO: TEMP! should be [self._world.yglp, self._world.ygrp]
            self._actions.search([self.goalpost_to_track], center_on_targets=False).onDone(self.onSearchResults)
        # Ball inside kicking area, kick it
        elif ball_location == BALL_IN_KICKING_AREA:
            self.debugPrint("Kicking!")
            if self.ENABLE_MOVEMENT:
                self._actions.tracker.stop()
                # by Vova - new kick
                #self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT, side).onDone(self.callOnDone)
                self.debugPrint("cntr_param: %3.3f" % (cntr_param))
                self._actions.adjusted_straight_kick(side, cntr_param)
        else:
            if ball_location == BALL_FRONT:
                self.debugPrint("Walking straight!")
                if self.ENABLE_MOVEMENT:
                    self._actions.changeLocationRelative(kp_x*MOVEMENT_PERCENTAGE).onDone(self.doNextAction)
            elif ball_location in (BALL_BETWEEN_LEGS, BALL_SIDE_NEAR):
                self.debugPrint("Side-stepping!")
                if self.ENABLE_MOVEMENT:
                    self._actions.changeLocationRelativeSideways(0.0, kp_y*MOVEMENT_PERCENTAGE, walk=moves.SIDESTEP_WALK).onDone(self.doNextAction)
            elif ball_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
                self.debugPrint("Turning!")
                if self.ENABLE_MOVEMENT:
                    self._actions.turn(kp_bearing*MOVEMENT_PERCENTAGE).onDone(self.doNextAction)
            else:
                self.debugPrint("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")
        
        if not self.ENABLE_MOVEMENT:
            self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)
    
    ####################################### STRAFING - BEGIN:
    def onSearchResults(self):
        self.debugPrint("onSearchResults")
        
        # Get world position from goal (to decide where to turn to)
        robot = self._world.robot
        world_pos = (robot.world_x, robot.world_y, robot.world_heading)
        dists = tuple(nicefloats([x.dist, x.focDist])
                    for x in self._world.team.target_posts.bottom_top)
        if not all(isinstance(x, float) for x in world_pos):
            self.debugPrint("ERROR: world position not computed. It is %r. dists are %s" % (world_pos, dists))
        else:
            self.debugPrint("position = %3.3f %3.3f %3.3f, dists %s" % (robot.world_x, robot.world_y, robot.world_heading, dists))
        
        self.debugPrint("manually centering on goalpost (from search goal results)")
        self.manualCentering(self.goalpost_to_track.centered_self, self.onSearchGoalDone)
        
    def onSearchGoalDone(self):
        self.goalLocationKnown = True
        # Track one of the goal posts (TODO: Add offset from post towards other post)
        self._actions.tracker.track(self.goalpost_to_track, self.onLostGoal)
        self.strafe()

    def onLostGoal(self):
        self.debugPrint("GOAL LOST, clearing footsteps, stopping strafing")
        self._actions.clearFootsteps()
        self.goalLocationKnown = False
        self.doNextAction()
    
    def strafe(self):
        if self.goalLocationKnown:
            if self.goalpost_to_track.bearing < -DEFAULT_CENTERING_Y_ERROR:
                self._actions.executeTurnCW().onDone(self.strafe)
            elif self.goalpost_to_track.bearing > DEFAULT_CENTERING_Y_ERROR:
                self._actions.executeTurnCCW().onDone(self.strafe)
            else:
                self.debugPrint("Aligned position reached! (starting ball search)")
                self._actions.tracker.stop()
                self.aligned_to_goal = True
                self.ballLocationKnown = False
                self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_BOTTOM).onDone(self.doNextAction)

    ####################################### STRAFING - END
