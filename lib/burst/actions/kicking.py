from math import cos, sin

from burst_util import (BurstDeferred, calculate_middle, calculate_relative_pos,
        polar2cart, cart2polar)
from events import (EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN,
    EVENT_CHANGE_LOCATION_DONE)
import actions
import burst.behavior_params as params
from consts import LEFT

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

    def __init__(self, eventmanager, actions, target_bearing_distance=None):
        super(BallKicker, self).__init__(None)
        if target_bearing_distance is not None:
            raise NotImplemented('BallKicker can only hit the goal right now')
        self._eventmanager = eventmanager
        self._actions = actions
        self._world = eventmanager._world
    
    def start(self):
        self.kp = None
        self.cachedBallDist = None
        self.cachedBallBearing = None
        self.cachedBallElevation = None
        self.goal = None
        self.doBallTracking = False
        self.searchLevel = actions.LOOKAROUND_QUICK
        
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        
        self._actions.initPoseAndStiffness().onDone(self.doNextAction)
        
    def onKickDone(self):
#        for event in [EVENT_BALL_IN_FRAME, EVENT_ALL_YELLOW_GOAL_SEEN,
#                        EVENT_CHANGE_LOCATION_DONE]:
#            self._eventmanager.unregister(event)
        self.callOnDone()
        
    def searchBallAndGoal(self, searchLevel):
        self.doBallTracking = False
        # TODO: Fix YELLOW to use opponent goal
        self._eventmanager.register(EVENT_ALL_YELLOW_GOAL_SEEN, self.onGoalSeen)
        self._actions.lookaround(searchLevel).onDone(self.onScanDone)

    def onBallInFrame(self):
        #print "Ball seen!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        # do ball tracking
        if self.doBallTracking:
            self._actions.executeTracking(self._world.ball)

        # Keep updating cached ball position for kicking-point
        self.cachedBallDist = self._world.ball.distSmoothed
        self.cachedBallBearing = self._world.ball.bearing
        self.cachedBallElevation = self._world.ball.elevation
        #print "Ball seen at dist/bearing/elevation: %3.3f %3.3f %3.3f" % (self.cachedBallDist, self.cachedBallBearing, self.cachedBallElevation)
        
    def onScanDone(self):
        print "\nScan done!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        print "******************"
        
        self._eventmanager.unregister(EVENT_ALL_YELLOW_GOAL_SEEN)
        
        # if both goal and ball seen during scan
        # TODO: NEED TO REPLACE WITH AND, changed temporarily for just going to ball
        if self.goal or self.cachedBallDist:
            self._actions.changeHeadAnglesRelative(self.cachedBallBearing, -self.cachedBallElevation, 1.0).onDone(self.calcKP)
        else:
            # otherwise, do a more thorough scan
            print "goal and ball NOT seen, searching again..."
            self.searchLevel = actions.LOOKAROUND_FRONT
            self.searchBallAndGoal(self.searchLevel)
    
    def calcKP(self):
        self.doBallTracking = True
        
        if self.goal and self.cachedBallDist:
            print "goal and ball seen, moving head in ball direction"
            # compute kicking-point
            #goal = self.calculate_middle(self._team.left_post, self._team.right_post)
            ball = (self.cachedBallDist * cos(self.cachedBallBearing), self.cachedBallDist * sin(self.cachedBallBearing))
            self.kp = calculate_relative_pos(ball, self.goal, params.KICK_OFFSET_FROM_BALL)
            print "self.kp: ", self.kp
        elif self.cachedBallDist:
            ################## TODO: remove following, temporary for testing ########################################################################
            print "ball seen, moving head in ball direction"
            self.kp = True
        
        self.doNextAction()
    
    def onGoalSeen(self):
        if self.goal is None:
            self.goal = calculate_middle((self._world.team.left_post.dist, self._world.team.left_post.bearing),
                                          (self._world.team.right_post.dist, self._world.team.right_post.bearing))
            print self.goal

    def doNextAction(self):
        print "\nDeciding on next move: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        print "------------------"

        # if kicking-point is not known, search for it
        if self.kp is None:
            print "kicking-point unknown, searching for ball & opponent goal"
            # do a quick search for kicking point
            self.searchLevel = actions.LOOKAROUND_QUICK
            self.searchBallAndGoal(self.searchLevel)
            return

        if not self._world.ball.seen:
            print "BALL NOT SEEN!"

        # ball is visible, let's approach it

        # for now, just directly approach ball and kick it wherever
        ballBearing = self._world.ball.bearing
        ballDist = self._world.ball.distSmoothed
        
        (ball_x, ball_y) = polar2cart(ballDist, ballBearing)
        print "ball_x: %3.3fcm, ball_y: %3.3fcm" % (ball_x, ball_y)
        
        # determine kicking leg
        side = ballBearing < 0 # 0 = LEFT, 1 = RIGHT
        if (side == LEFT): print "LEFT"
        else: print "RIGHT"

        #(target_x, target_y) = (ball_x - (KICK_X_MIN[side] + KICK_X_MAX[side])/2, ball_y + (KICK_Y_MIN[side] + KICK_Y_MAX[side])/2)
        (target_x, target_y) = (ball_x - params.KICK_X_OPT[side], ball_y - params.KICK_Y_OPT[side])
        print "target_x: %3.3fcm   target_y: %3.3fcm" % (target_x, target_y)

        (target_dist, target_bearing) = cart2polar(target_x, target_y)
        print "target_dist: %3.3fcm   target_bearing: %3.3f" % (target_dist, target_bearing)

        print "KICK_X_MIN[side]: %3.3f" % params.KICK_X_MIN[side]
        print "KICK_X_MAX[side]: %3.3f" % params.KICK_X_MAX[side]
        print "KICK_Y_MIN[side]: %3.3f" % params.KICK_Y_MIN[side]
        print "KICK_Y_MAX[side]: %3.3f" % params.KICK_Y_MAX[side]
        
        # Ball inside kicking area, kick it
        if (params.KICK_X_MIN[side] < ball_x < params.KICK_X_MAX[side]) and (abs(params.KICK_Y_MIN[side]) < abs(ball_y) < abs(params.KICK_Y_MAX[side])):
            print "Kicking!"
            self.doKick(side)
            return
        else:
            # Ball between legs, advance using straight+sideways
            if abs(ball_y) < abs(params.KICK_Y_MIN[side]):
                print "Ball between legs!"
            pass
        
        # TODO: REMOVE!!!
        self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now
        return

#        # target x,y are computed as the difference between the ball bearing/dist and the optimal kick bearing/dist
#        target_x = ballDist * cos(ballBearing) - params.KICK_DIST_MIN[side] * cos(params.KICK_BEARING_MIN[side])
#        target_y = ballDist * sin(ballBearing) - params.KICK_DIST_MIN[side] * sin(params.KICK_BEARING_MIN[side])
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
#                    print "Bearing OK, Distance large -> advancing straight (half way)"
##                    self._actions.changeLocationRelative(target_x*3/4, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now
#                elif abs(target_bearing) > KICK_TURN_ANGLE/4:
#                    # if bearing too large, use side-stepping to advance
#                    print "Bearing a little large, Distance OK -> advancing sideways only"
##                    self._actions.changeLocationRelativeSideways(0, target_y*3/4).onDone(self.doNextAction)
#                else:
#                    # if near ball, use forward/side-stepping to advance
#                    print "Bearing almost OK, Distance almost OK -> advance straight with sideways"
##                    self._actions.changeLocationRelativeSideways(target_x*3/4, target_y*3/4).onDone(self.doNextAction)
            
        # TODO: REMOVE!!!
        self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now

    def doKick(self, side):
        self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
        
        self._actions.kick(actions.KICK_TYPE_STRAIGHT, side).onDone(self.onKickDone)
        
#        if self._world.ball.bearing > 0.0:
#            # Kick with left
#            print "Left kick!"
#            self._actions.kick(actions.KICK_TYPE_STRAIGHT_WITH_LEFT).onDone(self.onKickDone)
#        else:
#            # Kick with right
#            print "Right kick!"
#            self._actions.kick(actions.KICK_TYPE_STRAIGHT_WITH_RIGHT).onDone(self.onKickDone)



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
#            walk = moves.FASTEST_WALK)

#    def doTestFinalKP(self):
#        print "\nTest info: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
#        
#        (target_x, target_y) = self.convertBallPosToFinalKickPoint(self._world.ball.distSmoothed, self._world.ball.bearing)
#        print "Final Kick point: (target_x: %3.3fcm, target_y: %3.3fcm)" % (target_x, target_y)
#
#        if target_x <= KICK_MINIMAL_DISTANCE_X and abs(target_y) <= KICK_MINIMAL_DISTANCE_Y:
#            print "KICK POSSIBLE! *********************************************************"
