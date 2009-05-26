#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.events import EVENT_BALL_IN_FRAME, EVENT_BALL_SEEN, EVENT_BALL_LOST, EVENT_CHANGE_LOCATION_DONE, EVENT_ALL_YELLOW_GOAL_SEEN
from burst.consts import DEG_TO_RAD, IMAGE_HALF_WIDTH, IMAGE_HALF_HEIGHT
from burst.player import Player
import burst.actions as actions
import burst.moves as moves
from burst.world import World
from math import cos, sin
from burst_util import calculate_middle, calculate_relative_pos, polar2cart, cart2polar

"""
    Logic for Kicker:

1. Scan for goal & ball
2. Calculate kicking-point (correct angle towards opponent goal), go as quickly as possible towards it (turn-walk-turn)
3. When near ball, go only straight and side-ways (align against leg closer to ball, and use relevant kick)
4. When close enough - kick!

Add states? add "closed-loop" (ball moved detection, robot moves incorrectly detection)

TODO:
Add "k-p relevant" flag (to be made FALSE on start, when ball moves). Might not be necessary once localization kicks in
Take bearing into account when kicking
When finally approaching ball, use sidestepping instead of turning (only for a certain degree difference)
When calculating k-p, take into account the kicking leg (use the one closer to opponent goal)

Add ball position cache (same as k-p local cache)
Handle negative target location (walk backwards instead of really big turns...)
What to do when near ball and k-p wasn't calculated?
Handle case where ball isn't seen after front scan (add full scan inc. turning around) - hopefully will be overridden with ball from comm.
Obstacle avoidance
"""

#if World.connected_to_nao:
    #KICK_MINIMAL_DISTANCE_X = 1.3*4 #1.6 is closest perceivable distance (x)
    #KICK_MINIMAL_DISTANCE_Y = 0.3*2 #0.3 is closest perceivable bearing (y)
    # values that minimizes KICK_MINIMAL_DISTANCE_X and KICK_MINIMAL_DISTANCE_Y (yet keeps them POSITIVE)
    #KICK_DIST_FROM_BALL = 13.0
    #KICK_OFFSET_MID_BODY = 0.3
#else: #World.connected_to_webots
    #KICK_MINIMAL_DISTANCE_X = 1.1
    #KICK_MINIMAL_DISTANCE_Y = 1.2
    # values that minimizes KICK_MINIMAL_DISTANCE_X and KICK_MINIMAL_DISTANCE_Y (yet keeps them POSITIVE)
    #KICK_DIST_FROM_BALL = 31.0
    #KICK_OFFSET_MID_BODY = 1.0

''' Kick consts (Measurements acquired via headTrackingTester)
# First value is for LEFT, second for RIGHT
BEARING_MIN = minimal kicking bearing (as centralized as possible) - best possible straight kick
BEARING_RANGE = maximal kicking bearing (delta from min, to either direction) - not centralized, yet still acceptable kick
DIST_MIN = minimal kicking distance (as close to leg as possible) - best possible straight kick
DIST_RANGE = maximal kicking distance (delta from min) - farther away from leg, yet still acceptable kick
'''
LEFT = 0
RIGHT = 1
if World.connected_to_nao:
#    KICK_BEARING_MIN = (0.25, -0.33) 
#    KICK_BEARING_RANGE = (0.081, 0.081) #(-0.081, 0.081)
#    KICK_DIST_MIN = (15.6, 15.6)
#    KICK_DIST_RANGE = (4.4, 3.4)
    KICK_X_MIN = (28.0,28.0)
    KICK_X_MAX = (32.5,32.5)
    KICK_Y_MIN = (6.0,-13.0)
    KICK_Y_MAX = (13.0,-6.0)
else: #World.connected_to_webots
#    KICK_BEARING_MIN = (0.30, -0.30)
#    KICK_BEARING_RANGE = (0.10, 0.10)
#    KICK_DIST_MIN = (30.0, 30.0)
#    KICK_DIST_RANGE = (2.0, 2.0)
    KICK_X_MIN = (28.0,28.0)
    KICK_X_MAX = (32.5,32.5)
    KICK_Y_MIN = (6.0,-13.0)
    KICK_Y_MAX = (13.0,-6.0)
    
KICK_X_OPT = ((KICK_X_MAX[LEFT]+KICK_X_MIN[LEFT])/2, (KICK_X_MAX[RIGHT]+KICK_X_MIN[RIGHT])/2)
KICK_Y_OPT = ((KICK_Y_MAX[LEFT]+KICK_Y_MIN[LEFT])/2, (KICK_Y_MAX[RIGHT]+KICK_Y_MIN[RIGHT])/2)

KICK_TURN_ANGLE = 45 * DEG_TO_RAD
KICK_SIDEWAYS_DISTANCE = 10.0

#KICK_TARGET_X = (cos(KICK_BEARING_MIN[LEFT]+KICK_BEARING_RANGE[LEFT]/2)*(KICK_DIST_MIN[LEFT]+KICK_DIST_RANGE[LEFT]/2), 
#                 cos(KICK_BEARING_MIN[RIGHT]+KICK_BEARING_RANGE[RIGHT]/2)*(KICK_DIST_MIN[RIGHT]+KICK_DIST_RANGE[RIGHT]/2))
#
#KICK_TARGET_Y = (sin(KICK_BEARING_MIN[LEFT]+KICK_BEARING_RANGE[LEFT]/2)*(KICK_DIST_MIN[LEFT]+KICK_DIST_RANGE[LEFT]/2), 
#                 sin(KICK_BEARING_MIN[RIGHT]+KICK_BEARING_RANGE[RIGHT]/2)*(KICK_DIST_MIN[RIGHT]+KICK_DIST_RANGE[RIGHT]/2))
#
#print "KICK_TARGET_X: %3.3fcm, %3.3fcm" % (KICK_TARGET_X[LEFT], KICK_TARGET_X[RIGHT])
#print "KICK_TARGET_Y: %3.3fcm, %3.3fcm" % (KICK_TARGET_Y[LEFT], KICK_TARGET_Y[RIGHT])

#CAMERA_BEARING_OFFSET = 0.04 # cech = 0.04

OFFSET_FROM_BALL = 12

class Kicker(Player):
    
    def onStart(self):
        self.kp = None
        self.cachedBallDist = None
        self.cachedBallBearing = None
        self.cachedBallElevation = None
        self.goal = None
        self.doBallTracking = False
        self.searchLevel = actions.LOOKAROUND_QUICK
        
        self._eventmanager.unregister_all()

        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        
        self._actions.initPoseAndStiffness()
        
        self.doNextAction()
        # TESTING:
        ##self._eventmanager.setTimeoutEventParams(2.0, cb=self.doTestFinalKP)
        
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
        
        # if both goal and ball seen during scan
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
            self.kp = calculate_relative_pos(ball, self.goal, OFFSET_FROM_BALL)
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

#        if not self._world.ball.seen:
#            print "BALL NOT SEEN!"

        # ball is visible, let's approach it

        # for now, just directly approach ball and kick it wherever (closed-loop style)
        ballBearing = self._world.ball.bearing
        ballDist = self._world.ball.distSmoothed
        
        (ball_x, ball_y) = polar2cart(ballDist, ballBearing)
        print "ball_x: %3.3fcm, ball_y: %3.3fcm" % (ball_x, ball_y)
        
        # determine kicking leg
        side = ballBearing < 0 # 0 = LEFT, 1 = RIGHT
        if (side == LEFT):
            print "LEFT"
        else:
            print "RIGHT"

        #(target_x, target_y) = (ball_x - (KICK_X_MIN[side] + KICK_X_MAX[side])/2, ball_y + (KICK_Y_MIN[side] + KICK_Y_MAX[side])/2)
        (target_x, target_y) = (ball_x - KICK_X_OPT[side], ball_y + KICK_Y_OPT[side])
        print "target_x: %3.3fcm   target_y: %3.3fcm" % (target_x, target_y)

        (target_dist, target_bearing) = cart2polar(target_x, target_y)
        print "target_dist: %3.3fcm   target_bearing: %3.3f" % (target_dist, target_bearing)

        print "KICK_X_MIN[side]: %3.3f" % KICK_X_MIN[side]
        print "KICK_X_MAX[side]: %3.3f" % KICK_X_MAX[side]
        print "KICK_Y_MIN[side]: %3.3f" % KICK_Y_MIN[side]
        print "KICK_Y_MAX[side]: %3.3f" % KICK_Y_MAX[side]

        # Ball inside kicking area, kick it
        if (KICK_X_MIN[side] < ball_x < KICK_X_MAX[side]) and (KICK_Y_MIN[side] < ball_y < KICK_Y_MAX[side]):
            print "Kicking!"
#            self.doKick()
#            return
        else:
            pass
        

        

        # TODO: REMOVE!!!
        self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now
        return

        
        
        
        
        
        # target x,y are computed as the difference between the ball bearing/dist and the optimal kick bearing/dist
        target_x = ballDist * cos(ballBearing) - KICK_DIST_MIN[side] * cos(KICK_BEARING_MIN[side])
        target_y = ballDist * sin(ballBearing) - KICK_DIST_MIN[side] * sin(KICK_BEARING_MIN[side])
        print "target_x: %3.3fcm   target_y: %3.3fcm" % (target_x, target_y)
        
        (target_dist, target_bearing) = cart2polar(target_x, target_y)
        print "target_dist: %3.3fcm   target_bearing: %3.3f" % (target_dist, target_bearing)

        # TODO: USE JUST X,Y FOR ENTIRE LOGIC?
        
        # Ball inside kicking area, kick it
        if ballDist < (KICK_DIST_MIN[side] + KICK_DIST_RANGE[side]) and \
                (KICK_BEARING_MIN[side]-KICK_BEARING_RANGE[side] < ballBearing < KICK_BEARING_MIN[side]+KICK_BEARING_RANGE[side]):
            print "Kicking!"
#            self.doKick()
        else:
            # Ball between legs, advance using straight+sideways
            if (side == LEFT and KICK_BEARING_MIN[side]-KICK_BEARING_RANGE[side] > ballBearing) or \
                (side == RIGHT and KICK_BEARING_MIN[side]+KICK_BEARING_RANGE[side] < ballBearing):
                print "Ball between legs!"            
            
            # Ball bearing too large, turn towards ball
            if abs(target_bearing) > KICK_TURN_ANGLE:
                print "Bearing too large, Distance ignored -> turning towards ball!"
#                self._actions.turn(target_bearing*3/4).onDone(self.doNextAction)
            else:
                if target_dist > KICK_SIDEWAYS_DISTANCE:
                    # if away from ball, advance half-way without turning/side-stepping
                    print "Bearing OK, Distance large -> advancing straight (half way)"
#                    self._actions.changeLocationRelative(target_x*3/4, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now
                elif abs(target_bearing) > KICK_TURN_ANGLE/4:
                    # if bearing too large, use side-stepping to advance
                    print "Bearing a little large, Distance OK -> advancing sideways only"
#                    self._actions.changeLocationRelativeSideways(0, target_y*3/4).onDone(self.doNextAction)
                else:
                    # if near ball, use forward/side-stepping to advance
                    print "Bearing almost OK, Distance almost OK -> advance straight with sideways"
#                    self._actions.changeLocationRelativeSideways(target_x*3/4, target_y*3/4).onDone(self.doNextAction)
            
        # TODO: REMOVE!!!
        self._actions.changeLocationRelative(0, 0, 0).onDone(self.doNextAction) # removed target_x/2 for now

    def doKick(self):
        self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
        
        if self._world.ball.bearing > 0.0:
            # Kick with left
            print "Left kick!"
            self._actions.kick(actions.KICK_TYPE_STRAIGHT_WITH_LEFT).onDone(self._eventmanager.quit)
        else:
            # Kick with right
            print "Right kick!"
            self._actions.kick(actions.KICK_TYPE_STRAIGHT_WITH_RIGHT).onDone(self._eventmanager.quit)
        
        # TEMP
        #self._actions.sitPoseAndRelax()
        self._eventmanager.quit()


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

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
