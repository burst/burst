#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.events import EVENT_BALL_IN_FRAME, EVENT_BALL_SEEN, EVENT_BALL_LOST
from burst.consts import DEG_TO_RAD
from burst.player import Player
from burst.events import *
from burst.consts import *
import burst.actions as actions
import burst.moves as moves
from burst.world import World
from math import cos, sin
"""
    Logic for Kicker:

1. Scan for goal & ball
2. Calculate kicking-point (correct angle towards opponent goal), go as quickly as possible towards it (turn-walk-turn)
3. When near ball, go only straight and side-ways (align against leg closer to ball, and use relevant kick)
4. When close enough - kick!

Keep using head to track once ball is found? will interfere with closed-loop

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
    KICK_DIST_FROM_BALL = 31.0
    KICK_OFFSET_MID_BODY = 1.0
    KICK_NEAR_BALL_DISTANCE_X = 10.0
    KICK_NEAR_BALL_DISTANCE_Y = 10.0
    
class kicker(Player):

    def onStart(self):
        self.kp = None
        self.kpBallDist = None
        self.kpBallBearing = None
        self.kpBallElevation = None
        
        self._eventmanager.unregister_all()
        self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
        self._actions.initPoseAndStiffness()
        
        # TESTING:
        #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        #if (not self.kp is None):
        #    print "self.kp is known, moving head in kpBall direction"
        #    self.doMoveHead(self.kpBallBearing, -self.kpBallElevation)
        ##self._eventmanager.setTimeoutEventParams(2.0, cb=self.doTestKP)
        
        # do a quick search for kicking point
        self._actions.scanQuick().onDone(self.onScanDone)
        
        #self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        #self._actions.changeLocationRelativeSideways(20, 20)

    def doTestKP(self):
        print "\nTest info: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        
        (target_x, target_y) = self.convertBallPosToFinalKickPoint(self._world.ball.distSmoothed, self._world.ball.bearing)
        print "Final Kick point: (target_x: %3.3fcm, target_y: %3.3fcm)" % (target_x, target_y)

        if target_x <= KICK_MINIMAL_DISTANCE_X and abs(target_y) <= KICK_MINIMAL_DISTANCE_Y:
            print "KICK POSSIBLE! *********************************************************"

    def onScanDone(self):
        print "\nScan done!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        print "******************"
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        if (not self.kp is None):
            print "self.kp is known, moving head in kpBall direction"
            
            self.doMoveHead(self.kpBallBearing, -self.kpBallElevation)
        
        self.doNextAction()
    
    def doNextAction(self):
        print "\nDeciding on next move: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        print "------------------"

        # if kicking-point is not known, search for it
        if self.kp is None:
            print "kicking-point unknown, searching for ball & opponent goal"
            self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
            self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
            # TODO: change to scan around
            self._actions.scanFront().onDone(self.onScanDone)
            return

        if not self._world.ball.seen:
            print "BALL NOT SEEN!"
            # TODO: do another scan OR use bearing and distance from k-p???
#            print "ball location unknown, searching for ball & opponent goal"
#            self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
#            self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
#            # TODO: change to scan around
#            self._actions.scanFront().onDone(self.onScanDone)
            #return
        
        # ball is visible, let's approach it
        (target_x, target_y) = self.convertBallPosToFinalKickPoint(self._world.ball.distSmoothed, self._world.ball.bearing)
        print "Final Kick point: (target_x: %3.3fcm, target_y: %3.3fcm)" % (target_x, target_y)
        
        # if ball is far, advance (turn/forward/turn)
        if target_x > 50.0 or abs(target_y) > 50.0:
            self.gotoLocation(self.kp)
        else:
            # if ball within kick distance, kick it
            if target_x <= KICK_MINIMAL_DISTANCE_X and abs(target_y) <= KICK_MINIMAL_DISTANCE_Y: # target_x <= 1.0 and abs(target_y) <= 2.0
                self.doKick()
            # if ball is near us, advance (forward/side-stepping)
            elif target_x <= KICK_NEAR_BALL_DISTANCE_X and abs(target_y) <= KICK_NEAR_BALL_DISTANCE_Y:
                #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
                self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
                self._actions.changeLocationRelativeSideways(target_x, target_y)
            # if ball a bit far, advance (forward only)
            else: #if target_x <= 50.:
                self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
                self._actions.changeLocationRelativeSideways(target_x, 0.)
            

    def onKickingPointChanged(self):
        print "Kicking Point Changed!"
        # save first KP encountered
        computed = self._world.computed
        if computed.kp_valid:
            self._eventmanager.unregister(EVENT_KP_CHANGED)
            self.kp = computed.kp
            
            self.kpBallDist = self._world.ball.distSmoothed
            self.kpBallBearing = self._world.ball.bearing
            self.kpBallElevation = self._world.ball.elevation
            
            print "KP: %3.3f, %3.3f, %3.3f" % self.kp
            print "KP Ball dist/bearing/elevation: %3.3f %3.3f %3.3f" % (self.kpBallDist, self.kpBallBearing, self.kpBallElevation)
            
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
        
        #self._eventmanager.quit()
        #self._actions.sitPoseAndRelax()
    
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
    
    def onChangeLocationDone(self):
        print "Change Location Done!"
        self.doNextAction()
        
    def onBallInFrame(self):
        # do ball tracking
        if not self._world.robot.isHeadMotionInProgress():
            xNormalized = self.normalizeBallX(self._world.ball.centerX)
            yNormalized = self.normalizeBallY(self._world.ball.centerY)
            if abs(xNormalized) > 0.05 or abs(yNormalized) > 0.05:
                self.doBallTracking(xNormalized, yNormalized)

    def doBallTracking(self, xNormalized, yNormalized):
        CAM_X_TO_RAD_FACTOR = 23.2/2 * DEG_TO_RAD #46.4/2
        CAM_Y_TO_RAD_FACTOR = 17.4/2 * DEG_TO_RAD #34.8/2
        
        deltaHeadYaw = xNormalized * CAM_X_TO_RAD_FACTOR
        deltaHeadPitch = -yNormalized * CAM_Y_TO_RAD_FACTOR
        #self._actions.changeHeadAnglesRelative(deltaHeadYaw * DEG_TO_RAD + self._actions.getAngle("HeadYaw"), deltaHeadPitch * DEG_TO_RAD + self._actions.getAngle("HeadPitch")) # yaw (left-right) / pitch (up-down)
        
        self.doMoveHead(deltaHeadYaw, deltaHeadPitch)

    def doMoveHead(self, deltaHeadYaw, deltaHeadPitch):
        self._actions.changeHeadAnglesRelative(deltaHeadYaw, deltaHeadPitch) # yaw (left-right) / pitch (up-down)
        #print "deltaHeadYaw, deltaHeadPitch (rad): %3.3f, %3.3f" % (deltaHeadYaw, deltaHeadPitch)            
        #print "deltaHeadYaw, deltaHeadPitch (deg): %3.3f, %3.3f" % (deltaHeadYaw / DEG_TO_RAD, deltaHeadPitch / DEG_TO_RAD)

    def gotoLocation(self, target_location):
        print "Going to target location: %3.3f, %3.3f, %3.3f" % target_location 
        # ball is away, first turn and then approach ball
        delta_x, delta_y, delta_bearing = target_location
        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        return self._actions.changeLocationRelative(delta_x, delta_y, delta_bearing,
            walk_param = moves.FASTEST_WALK)


    ##################### Computational Methods #########################
   
    def normalizeBallX(self, ballX):
        return (IMAGE_HALF_WIDTH - ballX) / IMAGE_HALF_WIDTH # between 1 (left) to -1 (right)

    def normalizeBallY(self, ballY):
        return (IMAGE_HALF_HEIGHT - ballY) / IMAGE_HALF_HEIGHT # between 1 (top) to -1 (bottom)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(kicker).run()

