#!/usr/bin/python
from events import EVENT_BALL_IN_FRAME
from consts import DEG_TO_RAD

import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *
from burst.consts import *
import burst.actions as actions
import burst.moves as moves
from math import cos, sin
"""
    Logic for Kicker:

1. Scan for goal & ball
2. Calculate kicking-point (correct angle towards opponent goal), go as quickly as possible towards it (turn-walk-turn)
3. When near ball, go only straight and side-ways (align against leg closer to ball, and use relevant kick)
4. When close enough - kick!

Keep using head to track once ball is found? will interfere with closed-loop

TODO:
Take bearing into account when kicking
When finally approaching ball, use sidestepping instead of turning
When calculating k-p, take into account the kicking leg (use the one closer to opponent goal)

Add ball position cache (same as k-p local cache)
Handle negative target location (walk backwards instead of really big turns...)
What to do when near ball and k-p wasn't calculated?
Handle case where ball isn't seen after front scan (add full scan inc. turning around) - hopefully will be overridden with ball from comm.
Obstacle avoidance
"""

class kicker(Player):
    
    def onStart(self):
        self.kp = None
        self.kpBallDist = None
        self.kpBallBearing = None
        self.kpBallElevation = None
        
        self._eventmanager.unregister_all()
        self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
        self._actions.initPoseAndStiffness()
        
        # do a quick search for kicking point
        self._actions.scanQuick().onDone(self.onScanDone)
        
        #self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        #self._actions.changeLocationRelativeSideways(20, 20)

    def onScanDone(self):
        print "\nScan done!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        print "******************"
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        if (not self.kp is None):
            print "self.kp is known, moving head to kpBall direction"
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
            # if ball close enough, kick it
            if target_x <= 1.0 and abs(target_y) <= 1.2: # target_x <= 1.0 and abs(target_y) <= 2.0
                self.doKick()
            # if ball near us, advance (forward/side-stepping)
            elif target_x <= 10. and abs(target_y) <= 10.:
                #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
                self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
                self._actions.changeLocationRelativeSideways(target_x, target_y)
            # if ball a bit far, advance (forward only)
            elif target_x <= 50.:
                self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
                self._actions.changeLocationRelativeSideways(target_x, 0.)
            
#        if balldist <= 60:
#            self._actions.changeLocationRelativeSideways(target_x, target_y)
#            
#            if self._world.ball.dist > 35.0:
#                print "close to ball, but not enough, try to advance slowly"
#                close_kp = self.convertBallPosToFinalKickPoint(self._world.ball.dist, self._world.ball.bearing)
#                self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
#                self.gotoLocation(close_kp)
#            else:
#                print "Really close to ball"
#                self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
#                
#                if self._world.ball.dist >= 31.0:
#                    self.gotoLocation((34 - self._world.ball.dist, 0.0, 0.0))
#                else:
#                    print "Kicking!"
#                    self.doKick()
#                # TODO: add final positioning
#        else:
#            # get closer to ball
#            self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
#            self.gotoLocation(self.kp)

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
            self._actions.kick(actions.KICK_TYPE_STRAIGHT_WITH_LEFT)
        else:
            # Kick with right
            print "Right kick!"
            self._actions.kick(actions.KICK_TYPE_STRAIGHT_WITH_RIGHT)
        
        #self._eventmanager.quit()
        #self._actions.sitPoseAndRelax()
    
    # TODO: MOVE TO WORLD? ACTIONS? BALL? Needs to take into account selected kick & kicking leg...
    def convertBallPosToFinalKickPoint(self, dist, bearing):
        KICK_DIST_FROM_BALL = 31.0
        KICK_OFFSET_MID_BODY = 1.0
        if bearing < 0:
            KICK_OFFSET_MID_BODY *= -1

        cosBearing = cos(bearing)
        sinBearing = sin(bearing)
        target_x = cosBearing * (dist - KICK_DIST_FROM_BALL) + KICK_OFFSET_MID_BODY * sinBearing
        target_y = sinBearing * (dist - KICK_DIST_FROM_BALL) - KICK_OFFSET_MID_BODY * cosBearing
        
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
        xNormalized = self.normalizeBallX(self._world.ball.centerX)
        yNormalized = self.normalizeBallY(self._world.ball.centerY)
        if abs(xNormalized) > 0.05 or abs(yNormalized) > 0.05:
            self.doBallTracking(xNormalized, yNormalized)

    def doMoveHead(self, deltaHeadYaw, deltaHeadPitch):
        if not self._world.robot.isHeadMotionInProgress():
            #print "deltaHeadYaw, deltaHeadPitch (rad): %3.3f, %3.3f" % (deltaHeadYaw, deltaHeadPitch)            
            #print "deltaHeadYaw, deltaHeadPitch (deg): %3.3f, %3.3f" % (deltaHeadYaw / DEG_TO_RAD, deltaHeadPitch / DEG_TO_RAD)
            self._actions.changeHeadAnglesRelative(deltaHeadYaw, deltaHeadPitch) # yaw (left-right) / pitch (up-down)
        #else:
        #    print "HEAD MOTION ALREADY IN PROGRESS"

    def doBallTracking(self, xNormalized, yNormalized):
        CAM_X_TO_RAD_FACTOR = 23.2/2 * DEG_TO_RAD #46.4/2
        CAM_Y_TO_RAD_FACTOR = 17.4/2 * DEG_TO_RAD #34.8/2
        
        deltaHeadYaw = xNormalized * CAM_X_TO_RAD_FACTOR
        deltaHeadPitch = -yNormalized * CAM_Y_TO_RAD_FACTOR
        #self._actions.changeHeadAnglesRelative(deltaHeadYaw * DEG_TO_RAD + self._actions.getAngle("HeadYaw"), deltaHeadPitch * DEG_TO_RAD + self._actions.getAngle("HeadPitch")) # yaw (left-right) / pitch (up-down)
        # TODO: what happens when we give a new angle without waiting for the previous to be done?
        self.doMoveHead(deltaHeadYaw, deltaHeadPitch)

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
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(kicker).run()

