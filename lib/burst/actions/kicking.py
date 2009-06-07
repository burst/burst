from burst_util import (BurstDeferred, calculate_middle, calculate_relative_pos, polar2cart, cart2polar)

# local imports
import burst
from burst.events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN, EVENT_CHANGE_LOCATION_DONE)
import burst.actions
import burst.moves as moves
from burst.behavior_params import (KICK_X_OPT, KICK_Y_OPT, KICK_X_MIN, KICK_X_MAX, KICK_Y_MIN, KICK_Y_MAX, 
                                   calcBallArea, BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT, 
                                   BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL)
from burst_consts import LEFT, RIGHT

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
    DISABLE_MOVEMENT = False

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
        self.goal = None
        self._actions.initPoseAndStiffness().onDone(self.initKickerPosition)
        
    def initKickerPosition(self):
        self._actions.executeMoveRadians(moves.STRAIGHT_WALK_INITIAL_POSE).onDone(self.doNextAction)
        
    def searchBall(self):
        #self._actions.tracker.stop() # needed???
        self._actions.search([self._world.ball]).onDone(self.onSearchBallOver)

    def onSearchBallOver(self):
        # Ball found, track it
        self._actions.track(self._world.ball, self.onLostBall)
        self.ballLocationKnown = True
        self.doNextAction()
        
    def onLostBall(self):
        self.debugPrint("BALL LOST, clearing footsteps")
        self._actions.clearFootsteps() # TODO: Check if possible to do this via post
        self.ballLocationKnown = False
        self.doNextAction()

    def doNextAction(self):
        self.debugPrint("\nDeciding on next move: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (
            self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing))
        self.debugPrint("-"*100)

        # if kicking-point is not known, search for it
        if not self.ballLocationKnown:
            if self._world.ball.seen:
                self.debugPrint("Ball seen, tracking ball!")
                self.ballLocationKnown = True
                self._actions.track(self._world.ball, self.onLostBall)
            else:
                self.debugPrint("Ball not seen, searching for ball")
                # do a quick search for kicking point
                self.searchBall()
                return

        # for now, just directly approach ball and kick it wherever
        ballBearing = self._world.ball.bearing
        ballDist = self._world.ball.distSmoothed
        (ball_x, ball_y) = polar2cart(ballDist, ballBearing)
        self.debugPrint("ball_x: %3.3fcm, ball_y: %3.3fcm" % (ball_x, ball_y))
        
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
        
        self.debugPrint("AREA: %s" % ('BALL_IN_KICKING_AREA', 'BALL_BETWEEN_LEGS', 'BALL_FRONT', 'BALL_SIDE_NEAR', 'BALL_SIDE_FAR', 'BALL_DIAGONAL')[ball_location])
        
        # Ball inside kicking area, kick it
        if ball_location == BALL_IN_KICKING_AREA:
            self.debugPrint("Kicking!")
            if not self.DISABLE_MOVEMENT:
                self.doKick(side)
            
            # TODO: TEMP!!! "do nothing" move
            #self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)
            #return
        else:
            if ball_location == BALL_FRONT:
                self.debugPrint("Walking straight!")
                if not self.DISABLE_MOVEMENT:
                    self._actions.changeLocationRelative(kp_x*0.6).onDone(self.doNextAction)
            elif ball_location in (BALL_BETWEEN_LEGS, BALL_SIDE_NEAR):
                self.debugPrint("Side-stepping!")
                if not self.DISABLE_MOVEMENT:
                    self._actions.changeLocationRelativeSideways(0.0, kp_y, walk=moves.SIDESTEP_WALK).onDone(self.doNextAction)
            elif ball_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
                self.debugPrint("Turning!")
                if not self.DISABLE_MOVEMENT:
                    self._actions.turn(kp_bearing*0.6).onDone(self.doNextAction)
            else:
                self.debugPrint("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")
        
        if self.DISABLE_MOVEMENT:
            self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)
            
    def doKick(self, side):
        self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT, side).onDone(self.callOnDone)
