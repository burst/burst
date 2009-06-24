from math import cos, sin
from burst_util import (BurstDeferred, calculate_middle, calculate_relative_pos, polar2cart, cart2polar)

# local imports
import burst
from burst_events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN, EVENT_CHANGE_LOCATION_DONE)
import burst.actions
import burst.moves as moves
from burst.behavior_params import (KICK_X_OPT, KICK_Y_OPT,
                                   KICK_X_MIN, KICK_X_MAX, KICK_Y_MIN, KICK_Y_MAX,
                                   BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT_NEAR, BALL_FRONT_FAR, BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL)
from burst_consts import LEFT, RIGHT

#===============================================================================
#    Logic for Kicking behavior:
#
# 1. Scan for goal & ball
# 2. Calculate kicking-point (correct angle towards opponent goal), go as quickly as possible towards it (turn-walk-turn)
# 3. When near ball, go only straight and side-ways (align against leg closer to ball, and use relevant kick)
# 4. When close enough - kick!
#
#===============================================================================

#===============================================================================
# TODO's:
#
# 1. replace cachedBall... with values from world, since world does the same
#    (stores last seen when doesn't see the ball anymore)
# 2. add to world: keep last full ball position when ball within a certain frame
#    (away from outer-bound by threshold)
# 3. add multiple event registration support (not here... in eventmanager...)
#
# Add "ball moved" detection, robot moves incorrectly detection
# Add "k-p relevant" flag (to be made FALSE on start, when ball moves). Might not be necessary once localization kicks in
# Take bearing into account when kicking
# When finally approaching ball, use side-stepping instead of turning (only for a certain degree difference)
# When calculating k-p, take into account the kicking leg (use the one closer to opponent goal)
#
# Add ball position cache (same as k-p local cache)
# Handle negative target location (walk backwards instead of really big turns...)
# What to do when near ball and k-p wasn't calculated?
# Handle case where ball isn't seen after front scan (add full scan inc. turning around) - hopefully will be overridden with ball from comm.
# Obstacle avoidance
#
#===============================================================================

KICK_OFFSET_FROM_BALL = 12 # TODO: GAD: CORRECT THIS VALUE!

class passBall(BurstDeferred):

    verbose = True

    def __init__(self, eventmanager, actions):
        super(passBall, self).__init__(None)
        self._eventmanager = eventmanager
        self._actions = actions
        self._world = eventmanager._world

    def start(self):
        self.kp = None
        self.goal = None
        self.passingPoint = None
        #self._actions.initPoseAndStiffness().onDone(self.initKickerPosition)
        self.doNextAction()

    #def initKickerPosition(self):
        #self._actions.executeMove(moves.STABLE_WALK_INITIAL_POSE).onDone(self.doNextAction)

    def onKickDone(self):
#        for event in [EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN,
#                        EVENT_CHANGE_LOCATION_DONE]:
#            self._eventmanager.unregister(event)
        self.callOnDone()

    def searchBallAndGoal(self):
        self._actions.tracker.stop()
        # TODO - self._world.opponent_goal
        self._actions.search([self._world.ball, self._world.yglp, self._world.ygrp]).onDone(self.onSearchOver)

    def onSearchOver(self):
        # searched for ball and goal, goal is available - calculate middle point for kick point calculation.
        results = self._actions.searcher.results
        left_post, right_post = self._world.team.left_post, self._world.team.right_post
        ball = self._world.ball

        self.goal = calculate_middle((results[left_post].dist, results[left_post].bearing),
                                      (results[right_post].dist, results[right_post].bearing))
        # look at the ball directly
        self._actions.changeHeadAnglesRelative(results[ball].bearing, # TODO - constants!
                                               -results[ball].elevation*1.3, 1.0).onDone(self.calcKP)

    def onLostBall(self):
        # TODO: add ball lost handling
        print "BALL LOST"

    def calcKP(self):
        if self._world.ball.seen:
            self._actions.track(self._world.ball, self.onLostBall)
            results = self._actions.searcher.results
            ball_result = results[self._world.ball]

            dist = ball_result.distSmoothed
            bearing = ball_result.bearing

            if self.goal and ball_result.sighted:
                print "goal and ball seen, moving head in ball direction"
                # compute kicking-point
                #goal = self.calculate_middle(self._team.left_post, self._team.right_post)
                ball_xy = (dist * cos(bearing), dist * sin(bearing))
                (targ_x,targ_y) = self.goal
                if targ_x > 0:
                    self.passingPoint = (targ_x - 182.5, targ_y)
                else:
                    self.passingPoint = (targ_x + 182.5, targ_y)
                print "WHAT IS YOUR TARGET, MASTER?", self.passingPoint
                self.kp = calculate_relative_pos(ball_xy, self.passingPoint, KICK_OFFSET_FROM_BALL)
                print "self.kp: ", self.kp
            elif ball_result.sighted:
                ################## TODO: remove following, temporary for testing ########################################################################
                print "ball seen, moving head in ball direction"
                self.kp = True

        self.doNextAction()

    def doNextAction(self):
        if self.verbose:
            print "\nDeciding on next move: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
            print "------------------"

        # if kicking-point is not known, search for it
        if self.kp is None:
            print "kicking-point unknown, searching for ball & opponent goal"
            # do a quick search for kicking point
            self.searchBallAndGoal()
            return


        # for now, just directly approach ball and kick it wherever
        ballBearing = self._world.ball.bearing
        ballDist = self._world.ball.distSmoothed

        (ball_x, ball_y) = polar2cart(ballDist, ballBearing)
        if self.verbose:
            print "ball_x: %3.3fcm, ball_y: %3.3fcm" % (ball_x, ball_y)

        # determine kicking leg
        side = ballBearing < 0 # 0 = LEFT, 1 = RIGHT
        if self.verbose:
            if (side == LEFT): print "LEFT"
            else: print "RIGHT"

        #(target_x, target_y) = (ball_x - (KICK_X_MIN[side] + KICK_X_MAX[side])/2, ball_y + (KICK_Y_MIN[side] + KICK_Y_MAX[side])/2)
        (target_x, target_y) = (ball_x - KICK_X_OPT[side], ball_y - KICK_Y_OPT[side])
        if self.verbose:
            print "target_x: %3.3fcm   target_y: %3.3fcm" % (target_x, target_y)

        (target_dist, target_bearing) = cart2polar(target_x, target_y)
        if self.verbose:
            print "target_dist: %3.3fcm   target_bearing: %3.3f" % (target_dist, target_bearing)

        # ball location, as defined at behavior params (front, side, etc...)
        ball_location = self.calcBallArea(ball_x, ball_y, side)

        DEBUG_AREA = ('BALL_IN_KICKING_AREA', 'BALL_BETWEEN_LEGS', 'BALL_FRONT_NEAR', 'BALL_FRONT_FAR', 'BALL_SIDE_NEAR', 'BALL_SIDE_FAR', 'BALL_DIAGONAL')
        if self.verbose:
            print "AREA: %s" % DEBUG_AREA[ball_location]


        # REMOVE!!!!!!!!!!!!!!!!!!! used just for debugging different KICK_ parameters per robot
        if self.verbose:
            print "KICK_X_MIN: %3.3f" % KICK_X_MIN[0]


        # Ball inside kicking area, kick it
        if ball_location == BALL_IN_KICKING_AREA:
            print "Kicking!"

            self.doKick(side, target_dist)

            # TODO: TEMP!!! REMOVE!!!
            #self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)
            return
        else:
            print "advancing!"
            #self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)


    def calcBallArea(self, ball_x, ball_y, side):
        if (ball_x <= KICK_X_MAX[side]) and (abs(KICK_Y_MIN[side]) < abs(ball_y) <= abs(KICK_Y_MAX[side])): #KICK_X_MIN[side] <
            return BALL_IN_KICKING_AREA
        elif KICK_Y_MAX[RIGHT] < ball_y < KICK_Y_MAX[LEFT]:
            if ball_x <= KICK_X_MAX[side]:
                return BALL_BETWEEN_LEGS
            elif ball_x <= KICK_X_MAX[side]*3/2:
                return BALL_FRONT_NEAR
            else:
                return BALL_FRONT_FAR
        else: #if (ball_y > KICK_Y_MAX[LEFT] or ball_y < KICK_Y_MAX[RIGHT]):
            if ball_x <= KICK_X_MAX[side]:
                return BALL_SIDE_NEAR
            else: #ball_x > KICK_X_MAX[side]
                return BALL_DIAGONAL

    def doKick(self, side, target_distance):
        self._eventmanager.unregister(EVENT_BALL_IN_FRAME)

        self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT, side, target_distance).onDone(self.onKickDone)

