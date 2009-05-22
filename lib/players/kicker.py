#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.events import EVENT_BALL_IN_FRAME, EVENT_BALL_SEEN, EVENT_BALL_LOST, EVENT_KP_CHANGED, EVENT_CHANGE_LOCATION_DONE, EVENT_ALL_YELLOW_GOAL_SEEN
from burst.consts import DEG_TO_RAD, IMAGE_HALF_WIDTH, IMAGE_HALF_HEIGHT
from burst.player import Player
import burst.actions as actions
import burst.moves as moves
from burst.world import World
from math import cos, sin, sqrt, pi, fabs, atan, atan2

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

if World.connected_to_nao:
    KICK_MINIMAL_DISTANCE_X = 1.3*4 #1.6 is closest perceivable distance (x)
    KICK_MINIMAL_DISTANCE_Y = 0.3*2 #0.3 is closest perceivable bearing (y)
    KICK_DIST_FROM_BALL = 13.0
    KICK_OFFSET_MID_BODY = 0.3
    KICK_NEAR_BALL_DISTANCE_X = 10.0
    KICK_NEAR_BALL_DISTANCE_Y = 10.0
else:
    KICK_MINIMAL_DISTANCE_X = 1.1
    KICK_MINIMAL_DISTANCE_Y = 1.2
    KICK_DIST_FROM_BALL = 32.0
    KICK_OFFSET_MID_BODY = 1.0
    KICK_NEAR_BALL_DISTANCE_X = 10.0
    KICK_NEAR_BALL_DISTANCE_Y = 10.0
    
class kicker(Player):
    
    def onStart(self):
        self.kp = None
        self.cachedBallDist = None
        self.cachedBallBearing = None
        self.cachedBallElevation = None
        self.goal = None
        self.doBallTracking = False
        
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
        if self.goal and self.cachedBallDist:
            print "goal and ball seen, moving head in ball direction"
            self._actions.changeHeadAnglesRelative(self.cachedBallBearing, -self.cachedBallElevation)#.onDone(lambda:setattr(self,'doBallTracking',True))
            self.doBallTracking = True
            
            # compute kicking-point
            #goal = self.calculate_middle(self._team.left_post, self._team.right_post)
            ball = (self.cachedBallDist * cos(self.cachedBallBearing), self.cachedBallDist * sin(self.cachedBallBearing))
            self.kp = self.calculate_relative_pos(ball, self.goal, 12)
            print "self.kp: ", self.kp
            self.doNextAction()
        ################## TODO: remove following, temporary for testing ########################################################################
        elif self.cachedBallDist:
            print "goal and ball seen, moving head in ball direction"
            self._actions.changeHeadAnglesRelative(self.cachedBallBearing, -self.cachedBallElevation)
            self.doBallTracking = True
            self.kp = True
            self.doNextAction()
        else:
            # otherwise, do a more thorough scan
            print "goal and ball NOT seen, searching again..."
            self.searchLevel = actions.LOOKAROUND_FRONT
            self.searchBallAndGoal(self.searchLevel)
        
        return
        
    def onGoalSeen(self):
        if self.goal is None:
            self.goal = self.calculate_middle(self._world.team.left_post, self._world.team.right_post)
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

        # for now, just directly approach ball and kick it wherever (closed-loop style)

        # ball is visible, let's approach it
        (target_x, target_y) = self.convertBallPosToFinalKickPoint(self._world.ball.distSmoothed, self._world.ball.bearing)
        print "Final Kick point: (target_x: %3.3fcm, target_y: %3.3fcm)" % (target_x, target_y)
        
        bearingThreshold = actions.MINIMAL_CHANGELOCATION_TURN # TODO: MOVE TO CONSTS AT TOP
        distanceThreshold = KICK_MINIMAL_DISTANCE_X
        
        # TODO: Use either (x,y) or (dist,bearing), not both.
        #if self._world.ball.distSmoothed > KICK_DIST_FROM_BALL or bearing-difference-too-large:
        if target_x > KICK_MINIMAL_DISTANCE_X or abs(target_y) > KICK_MINIMAL_DISTANCE_Y:
            # if bearing isn't large or if near ball, don't turn and instead just advance
            if abs(self._world.ball.bearing) < bearingThreshold * 2 or self._world.ball.distSmoothed < KICK_DIST_FROM_BALL * 2:
                print "Advancing towards ball!"
                # if away from ball, advance half-way without turning/side-stepping
                if self._world.ball.distSmoothed > KICK_DIST_FROM_BALL*2:
                    print "only half way"
                    self._actions.changeLocationRelative(target_x/2, 0, 0).onDone(self.doNextAction)
#                elif self._world.ball.distSmoothed > KICK_DIST_FROM_BALL:
#                    print "all the way, just straight walk"
#                    self._actions.changeLocationRelative(target_x, 0, 0).onDone(self.doNextAction)
                else:
                    # if near ball, use forward/side-stepping to advance
                    print "all the way, including sideway walk"
                    self._actions.changeLocationRelativeSideways(target_x, target_y).onDone(self.doNextAction)
                
            elif abs(self._world.ball.bearing) > bearingThreshold:
                print "Turning towards ball!"
                self._actions.turn(self._world.ball.bearing).onDone(self.doNextAction)
                #self._actions.changeLocationRelative(0, 0, self._world.ball.bearing).onDone(self.doNextAction)
        else:
            print "Kicking!"
            self.doKick()

#        # if ball is far, advance (turn/forward/turn)
#        if target_x > 50.0 or abs(target_y) > 50.0:
#            self.gotoLocation(self.kp)
#        else:
#            # if ball within kick distance, kick it
#            if target_x <= KICK_MINIMAL_DISTANCE_X and abs(target_y) <= KICK_MINIMAL_DISTANCE_Y: # target_x <= 1.0 and abs(target_y) <= 2.0
#                self.doKick()
#            # if ball is near us, advance (forward/side-stepping)
#            elif target_x <= KICK_NEAR_BALL_DISTANCE_X and abs(target_y) <= KICK_NEAR_BALL_DISTANCE_Y:
#                #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
#                self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
#                self._actions.changeLocationRelativeSideways(target_x, target_y)
#            # if ball a bit far, advance (forward only)
#            else: #if target_x <= 50.:
#                self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
#                self._actions.changeLocationRelativeSideways(target_x, 0.)
            
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
        self._actions.sitPoseAndRelax()
        self._eventmanager.quit()
    
    # TODO: MOVE TO WORLD? ACTIONS? BALL? Needs to take into account selected kick & kicking leg...
    def convertBallPosToFinalKickPoint(self, dist, bearing):
        kick_offset_mid_body = bearing < 0 and -KICK_OFFSET_MID_BODY or KICK_OFFSET_MID_BODY

        cosBearing = cos(bearing)
        sinBearing = sin(bearing)
        # UGLY PATCH: the "/ 2" is a patch since ball perception near right/left optimal kicking point (on real Nao) do not seem symmetric.
        # ----------- we better use something like a (robot specific?) camera offset to fix this
        target_x = cosBearing * (dist - KICK_DIST_FROM_BALL) + kick_offset_mid_body * sinBearing / 2
        target_y = sinBearing * (dist - KICK_DIST_FROM_BALL) / 2 - kick_offset_mid_body * cosBearing
        
        if target_x > dist:
            print "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ do we have a problem here?"
            print "dist: %3.3f bearing: %3.3f" % (dist, bearing)
            print "target_x: %3.3f target_y: %3.3f" % (target_x, target_y) 
        
        return target_x, target_y

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


    ##################### Computational Methods #########################
   
    def normalizeBallX(self, ballX):
        return (IMAGE_HALF_WIDTH - ballX) / IMAGE_HALF_WIDTH # between 1 (left) to -1 (right)

    def normalizeBallY(self, ballY):
        return (IMAGE_HALF_HEIGHT - ballY) / IMAGE_HALF_HEIGHT # between 1 (top) to -1 (bottom)


    ### Calculate kicking-point, move functions to a utility class

    def calculate_middle(self, left_object, right_object):
        target_x = (right_object.dist * cos(right_object.bearing) + left_object.dist * cos(left_object.bearing)) / 2.0
        target_y = (right_object.dist * sin(right_object.bearing) + left_object.dist * sin(left_object.bearing)) / 2.0
        return (target_x, target_y)
    
    def calculate_relative_pos(self, (waypoint_x, waypoint_y), (target_x, target_y), offset):
        """ A point k distant (offset) from the waypoint (e.g., ball) along the line connecting the point 
        in the middle of the target (e.g., goal) and the waypoint in the outward direction.

        The coordinate system is the standard: the x axis is to the front,
        the y axis is to the left of the robot. The bearing is measured from the x axis ccw.
        
        computation:
         target - target center (e.g., middle of goal)
         waypoint - waypoint (e.g., ball) - should be of type Locatable (support dist/bearing
         normal - normal pointing from target (goal center) to waypoint (ball)
         result - return result (x, y, bearing)
        """
        
        normal_x, normal_y = waypoint_x - target_x, waypoint_y - target_y # normal is a vector pointing from center to ball
        normal_norm = sqrt(normal_x**2 + normal_y**2)
        normal_x, normal_y = normal_x / normal_norm, normal_y / normal_norm
        result_x, result_y = waypoint_x + offset * normal_x, waypoint_y + offset * normal_y
        #result_norm = (result_x**2 + result_y**2)**0.5
        result_bearing = atan2(-normal_y, -normal_x)
        #print "rel_pos: waypoint(%3.3f, %3.3f), target(%3.3f, %3.3f), n(%3.3f, %3.3f), result(%3.3f, %3.3f, %3.3f)" % (
        #    waypoint_x, waypoint_y, target_x, target_y, normal_x, normal_y, result_x, result_y, result_bearing)
        return result_x, result_y, result_bearing


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(kicker).run()
