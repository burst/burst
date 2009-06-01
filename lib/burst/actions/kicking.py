from math import cos, sin
from burst_util import (BurstDeferred, calculate_middle, calculate_relative_pos, polar2cart, cart2polar)

# local imports
import burst
from burst.events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN, EVENT_CHANGE_LOCATION_DONE)
import burst.actions
import burst.moves as moves
from burst.behavior_params import (KICK_OFFSET_FROM_BALL, KICK_X_OPT, KICK_Y_OPT, 
                                   KICK_X_MIN, KICK_X_MAX, KICK_Y_MIN, KICK_Y_MAX,
                                   BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT, BALL_SIDE, BALL_DIAGONAL)
from burst.consts import LEFT, RIGHT

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

class BallKicker(BurstDeferred):

    verbose = False

    def __init__(self, eventmanager, actions, target_bearing_distance=None):
        super(BallKicker, self).__init__(None)
        if target_bearing_distance is not None:
            raise NotImplemented('BallKicker can only hit the goal right now')
        self._eventmanager = eventmanager
        self._actions = actions
        self._world = eventmanager._world
    
    def start(self):
        self.kp = None
        self.goal = None
        self._actions.initPoseAndStiffness().onDone(self.doNextAction)
        
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
        print "WE LOST THE BALLLLLLL!!!!!!"

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
                self.kp = calculate_relative_pos(ball_xy, self.goal, KICK_OFFSET_FROM_BALL)
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

#        angles = []
#        old_change_angles_relative = self._actions.changeHeadAnglesRelative
#        def myChangeHeadAnglesRelative(*args, **kw):
#            angles.append(args)
#            #import pdb; pdb.set_trace()
#            print "="*10, angles
#            old_change_angles_relative(*args, **kw)
#        
#        self._actions.changeHeadAnglesRelative = myChangeHeadAnglesRelative

        #if not self._world.ball.seen:
        #    print "BALL NOT SEEN!"

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
        
        DEBUG_AREA = ('BALL_IN_KICKING_AREA', 'BALL_BETWEEN_LEGS', 'BALL_FRONT', 'BALL_SIDE', 'BALL_DIAGONAL')
        if self.verbose:
            print "AREA: %s" % DEBUG_AREA[ball_location]
        
        
        # REMOVE!!!!!!!!!!!!!!!!!!! used just for debugging different KICK_ parameters per robot
        if self.verbose:
            print "KICK_X_MIN: %3.3f" % KICK_X_MIN[0]
        
        
        # Ball inside kicking area, kick it
        if ball_location == BALL_IN_KICKING_AREA:
            print "Kicking!"
            self.doKick(side)
            
            # TODO: TEMP!!! REMOVE!!!
#            self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)
            return
        else:
            print "advancing!"
#            if ball_location == BALL_FRONT:
#                self._actions.changeLocationRelativeSideways(target_x*3/4).onDone(self.doNextAction)
#            elif ball_location in (BALL_SIDE, BALL_DIAGONAL):
#                self._actions.turn(target_bearing*2/3).onDone(self.doNextAction)
#            elif ball_location == BALL_BETWEEN_LEGS:
#                self._actions.changeLocationRelativeSideways(0.0, target_y*3/4, walk=moves.SIDESTEP_WALK).onDone(self.doNextAction)

            
################################### TESTING WALKS:
#            if ball_location == BALL_BETWEEN_LEGS:
#                self._actions.changeLocationRelativeSideways(0.0, target_y*3/4, walk=moves.SIDESTEP_WALK).onDone(self.doNextAction)
#                return
#            if ball_location == BALL_DIAGONAL:
#                self._actions.turn(target_bearing*2/3).onDone(self.doNextAction)
#                #self._actions.changeLocationRelative(target_x*3/4, 0.0, 0.0).onDone(self.doNextAction) # removed target_x/2 for now
#                return
                            
            #self._actions.changeLocationRelativeSideways(target_x*3/4, target_y*3/4).onDone(self.doNextAction)

######### TODO: TEMP!!! REMOVE!!!
            self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction)


#        elif ball_location == BALL_BETWEEN_LEGS:
#            print "Bearing almost OK, Distance small -> advancing straight (with side-stepping)"
#            self._actions.changeLocationRelativeSideways(target_x*3/4, target_y*3/4, 0).onDone(self.doNextAction)
#        elif ball_location == BALL_FRONT:
#            print "Bearing almost OK, Distance large -> advancing straight (without turning/side-stepping)"
#            self._actions.changeLocationRelative(target_x*3/4, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now
#        elif ball_location == BALL_SIDE:
#            print "Bearing too large, Distance ignored -> turning towards ball"
#            self._actions.turn(target_bearing*3/4).onDone(self.doNextAction)
#        else: #if ball_location == BALL_DIAGONAL:
#            print "Bearing almost OK, Distance small -> advancing straight (with side-stepping)"
#            self._actions.changeLocationRelative(target_x*3/4, target_y*3/4, 0).onDone(self.doNextAction)
            
        
#        # TODO: REMOVE!!!
#        self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now
#        return

#        # target x,y are computed as the difference between the ball bearing/dist and the optimal kick bearing/dist
#        target_x = ballDist * cos(ballBearing) - KICK_DIST_MIN[side] * cos(KICK_BEARING_MIN[side])
#        target_y = ballDist * sin(ballBearing) - KICK_DIST_MIN[side] * sin(KICK_BEARING_MIN[side])
#        print "target_x: %3.3fcm   target_y: %3.3fcm" % (target_x, target_y)
#        
#        (target_dist, target_bearing) = cart2polar(target_x, target_y)
#        print "target_dist: %3.3fcm   target_bearing: %3.3f" % (target_dist, target_bearing)
#
#        # Ball inside kicking area, kick it
#        if ballDist < (KICK_DIST_MIN[side] + KICK_DIST_RANGE[side]) and \
#                (KICK_BEARING_MIN[side]-KICK_BEARING_RANGE[side] < ballBearing < KICK_BEARING_MIN[side]+KICK_BEARING_RANGE[side]):
#            print "Kicking!"
##            self.doKick()
#        else:
#            # Ball between legs, advance using straight+sideways
#            if (side == LEFT and KICK_BEARING_MIN[side]-KICK_BEARING_RANGE[side] > ballBearing) or \
#                (side == RIGHT and KICK_BEARING_MIN[side]+KICK_BEARING_RANGE[side] < ballBearing):
#                print "Ball between legs!"            
#            
#            # Ball bearing too large, turn towards ball
#            if abs(target_bearing) > KICK_TURN_ANGLE:
#                print "Bearing too large, Distance ignored -> turning towards ball!"
##                self._actions.turn(target_bearing*3/4).onDone(self.doNextAction)
#            else:
#                if target_dist > KICK_SIDEWAYS_DISTANCE:
#                    # if away from ball, advance half-way without turning/side-stepping
#                    print "Bearing OK, Distance large -> advancing straight (not all the way)"
##                    self._actions.changeLocationRelative(target_x*3/4, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now
#                elif abs(target_bearing) > KICK_TURN_ANGLE/4:
#                    # if bearing too large, use side-stepping to advance
#                    print "Bearing a little large, Distance OK -> advancing sideways only"
##                    self._actions.changeLocationRelativeSideways(0, target_y*3/4).onDone(self.doNextAction)
#                else:
#                    # if near ball, use forward/side-stepping to advance
#                    print "Bearing almost OK, Distance almost OK -> advance straight with sideways"
##                    self._actions.changeLocationRelativeSideways(target_x*3/4, target_y*3/4).onDone(self.doNextAction)

    def calcBallArea(self, ball_x, ball_y, side):
        if (ball_x <= KICK_X_MAX[side]) and (abs(KICK_Y_MIN[side]) < abs(ball_y) <= abs(KICK_Y_MAX[side])): #KICK_X_MIN[side] < 
            return BALL_IN_KICKING_AREA
        elif KICK_Y_MIN[RIGHT] < ball_y < KICK_Y_MIN[LEFT] and ball_x <= KICK_X_MAX[side]:
            return BALL_BETWEEN_LEGS
        elif KICK_Y_MAX[RIGHT] < ball_y < KICK_Y_MAX[LEFT]:
            return BALL_FRONT
        else: #if (ball_y > KICK_Y_MAX[LEFT] or ball_y < KICK_Y_MAX[RIGHT]):
            if ball_x <= KICK_X_MAX[side]:
                return BALL_SIDE
            else: #ball_x > KICK_X_MAX[side]
                return BALL_DIAGONAL
            
    def doKick(self, side):
        self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
        
        self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT, side).onDone(self.onKickDone)

#        if self._world.ball.bearing > 0.0:
#            # Kick with left
#            print "Left kick!"
#            self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT_WITH_LEFT).onDone(self.onKickDone)
#        else:
#            # Kick with right
#            print "Right kick!"
#            self._actions.kick(burst.actions.KICK_TYPE_STRAIGHT_WITH_RIGHT).onDone(self.onKickDone)



#    def convertBallPosToFinalKickPoint(self, dist, bearing):
#        kick_leg = bearing < 0 # 0 = LEFT, 1 = RIGHT
#
#        cosBearing = cos(bearing)
#        sinBearing = sin(bearing)
#        target_x = cosBearing * (dist - KICK_TARGET_X[kick_leg]) + KICK_TARGET_Y[kick_leg] * sinBearing
#        target_y = sinBearing * (dist - KICK_TARGET_X[kick_leg]) - KICK_TARGET_Y[kick_leg] * cosBearing
#        
#        if target_x > dist:
#            print "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ do we have a problem here?"
#            print "dist: %3.3f bearing: %3.3f" % (dist, bearing)
#            print "target_x: %3.3f target_y: %3.3f" % (target_x, target_y) 
#        
#        return target_x, target_y

#    def onChangeLocationDone(self):
#        print "Change Location Done!"
#        self.doNextAction()

#    def gotoLocation(self, target_location):
#        print "Going to target location: %3.3f, %3.3f, %3.3f" % target_location 
#        # ball is away, first turn and then approach ball
#        delta_x, delta_y, delta_bearing = target_location
#        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
#        return self._actions.changeLocationRelative(delta_x, delta_y, delta_bearing,
#            walk = moves.STRAIGHT_WALK)

#    def doTestFinalKP(self):
#        print "\nTest info: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
#        
#        (target_x, target_y) = self.convertBallPosToFinalKickPoint(self._world.ball.distSmoothed, self._world.ball.bearing)
#        print "Final Kick point: (target_x: %3.3fcm, target_y: %3.3fcm)" % (target_x, target_y)
#
#        if target_x <= KICK_MINIMAL_DISTANCE_X and abs(target_y) <= KICK_MINIMAL_DISTANCE_Y:
#            print "KICK POSSIBLE! *********************************************************"
