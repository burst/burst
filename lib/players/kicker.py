#!/usr/bin/python

# TODO:
# Add slower walk when approaching ball (dynamic approach vs. static one)
# Align with goal for kick (need "around ball" movement), do camera switch for goal tracking? or use last goal position?
# Fix walk radius/arc issues
# Move consts somewhere nice
# add "ball lost" behavior (scan, etc.)
# Reality check

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

import time

class Kicker(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        self._eventmanager.register(EVENT_ALL_YELLOW_GOAL_SEEN, self.onGoalSeen)
        self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
        
    def onStop(self):
        super(Kicker, self).onStop()

    def onKickPointViable(self):
        print "Kick point viable:", self._world.computed.kp
        self._actions.kick()
        self._actions.sitPoseAndRelax()

    def onBallSeen(self):
        print "Ball Seen!"
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        #print "Ball x: %f" % self._world.ball.centerX
        #print "Ball y: %f" % self._world.ball.centerY
        
        self.test()

    def onChangeLocationDone(self):
        print "Change Location Done!"
        self._eventmanager.unregister(EVENT_CHANGE_LOCATION_DONE)
        if abs(self._world.ball.bearing) <= 0.1745 and self._world.ball.dist <= 20:
            self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
            self.onKickPointViable()
        else:
            print "we are still too far to kick the ball, advance towards ball again"
            #self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
            self.test()

        #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)

    def doBallTracking(self):
        xNormalized = (IMAGE_HALF_WIDTH - self._world.ball.centerX) / IMAGE_HALF_WIDTH # between 1 (left) to -1 (right)
        yNormalized = (IMAGE_HALF_HEIGHT - self._world.ball.centerY) / IMAGE_HALF_HEIGHT # between 1 (up) to -1 (down)
        if abs(xNormalized) > 0.05 or abs(yNormalized) > 0.05:
            X_TO_RAD_FACTOR = 23.2/2 * DEG_TO_RAD #46.4/2
            Y_TO_RAD_FACTOR = 17.4/2 * DEG_TO_RAD #34.8/2
            
            deltaHeadYaw = xNormalized * X_TO_RAD_FACTOR
            deltaHeadPitch = -yNormalized * Y_TO_RAD_FACTOR
            #self._actions.changeHeadAngles(deltaHeadYaw * DEG_TO_RAD + self._actions.getAngle("HeadYaw"), deltaHeadPitch * DEG_TO_RAD + self._actions.getAngle("HeadPitch")) # yaw (left-right) / pitch (up-down)
            # TODO: what happens when we give a new angle without waiting for the previous to be done?
            if not self._world.robot.isHeadMotionInProgress():
                self._actions.changeHeadAngles(deltaHeadYaw, deltaHeadPitch) # yaw (left-right) / pitch (up-down)
            else:
                print "doBallTracking: head still moving, not updating"

    def gotoAndKickBall(self):
        MINIMAL_KICKER_TURN = 0.1745
        print "goto ball and kick"
        # ball is away, first turn and then approach ball
        delta_y, delta_x, delta_bearing = self.kp # TODO: fix x,y issues
        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        self._actions.changeLocationRelative(delta_x, delta_y, delta_bearing)

    def onKickingPointChanged(self):
        self._eventmanager.unregister(EVENT_KP_CHANGED)
        self.kp = self._world.computed.kp
        print "KP: %3.3f, %3.3f, %3.3f" % self.kp
        print "self._world.ball.bearing: %f" % self._world.ball.bearing
        print "self._world.ball.dist: %f" % self._world.ball.dist
        
        self.gotoAndKickBall()
        
    def onBallInFrame(self):
        self.doBallTracking()
#        if self._world.robot.isMotionInProgress():
#            # robot is still walking / turning, return without doing anything
#            print "is walking: %f is turning: %f" % (self._world.robot.isWalkingActive, self._world.robot.isTurningActive)
#            return


    ##################### Debug Methods #########################

    def test(self):
        if self._world.robot.isHeadMotionInProgress():
            return
        
        self.kp = self.estimateKPwithoutGoal()
        
        print "KP: %3.3f, %3.3f, %3.3f" % self.kp
        print "self._world.ball.bearing: %f" % self._world.ball.bearing
        print "self._world.ball.dist: %f" % self._world.ball.dist
        
        self.gotoAndKickBall()
        
        
    def onGoalSeen(self):
        #print "Yellow goal seen"
        pass

    def onYetToBeCalledTurnDone(self):
        print "Turn Done!"
        self._eventmanager.unregister(EVENT_TURN_DONE)

        # TODO: move to consts
        BALL_APPROACH_DISTANCE = 35
        BALL_FAR_AWAY_DISTANCE = 100
        BALL_RADIUS = 10
        
        if self._world.ball.dist > BALL_APPROACH_DISTANCE:
            print "Starting to walk!"
            
            targetDistance = self._world.ball.dist - BALL_APPROACH_DISTANCE
            # if really far from ball, arrive to a location more distant from the ball (so we won't accidentally walk over the ball) 
            if self._world.ball.dist > BALL_FAR_AWAY_DISTANCE:
                targetDistance -= BALL_APPROACH_DISTANCE
            
            self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onWalkDone)
            self._actions.changeLocationRelative(self._world.ball.dist - BALL_RADIUS, 0, 0) # ball radius - update and re-position
        else:
            # ball is close, align with it carefully
            if abs(self._world.ball.bearing) <= 0.1745:
                self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
                self.onKickPointViable()
            else:
                # TODO do something meaningful
                pass
        
    def estimateKPwithoutGoal(self):
        # compute goal center bearing
        midGoalBearing = 0
        postsSeenCounter = 0
        if self._world.yglp.seen:
            print "self._world.yglp.bearing: %f" % self._world.yglp.bearing
            postsSeenCounter += 1
            midGoalBearing += self._world.yglp.bearing
        
        if self._world.ygrp.seen:
            print "self._world.ygrp.bearing: %f" % self._world.ygrp.bearing
            postsSeenCounter += 1
            midGoalBearing += self._world.ygrp.bearing
        
        if postsSeenCounter > 0:
            midGoalBearing = (self._world.yglp.bearing + self._world.ygrp.bearing)/postsSeenCounter
        print "midGoalBearing: %f" % midGoalBearing
        
        # determine if goal is left / right / center to ball
        bearingSum = self._world.ball.bearing + midGoalBearing
        bearingSumAbs = abs(self._world.ball.bearing) + abs(midGoalBearing)
        bearingProd = self._world.ball.bearing * midGoalBearing
        targetBearing = self._world.ball.bearing
        if bearingProd > 0:
            # ball and goal on same side
            if bearingSumAbs <  0.1745: # 10: --  bearing is radians (Vova)
                # ball and goal on same line (same sign, small sum)
                pass #targetBearing = self._world.ball.bearing
            else:
                # ball and goal on same side, far away (same sign, large sum)
                if abs(self._world.ball.bearing) > abs(midGoalBearing):
                    targetBearing *= 1.3
                else:
                    targetBearing *= 0.7
        else:
            # ball and goal on different sides
            if bearingSumAbs < 0.1745: # 10: --  bearing is radians (Vova)
                # ball and goal on roughly same line (different sign, small sum)
                if abs(self._world.ball.bearing) > abs(midGoalBearing):
                    targetBearing *= 1.2
                else:
                    targetBearing *= 0.8
            else:
                # ball and goal on same line (same sign, large sum)
                if abs(self._world.ball.bearing) > abs(midGoalBearing):
                    targetBearing *= 1.3
                else:
                    targetBearing *= 0.7

        #bearingOffset = (self._world.ball.bearing - midGoalBearing)/2.0
        #targetBearing = self._world.ball.bearing + bearingOffset * math.log(self._world.ball.dist - 33 + 1)/8.7
        
        print "self._world.ball.bearing: %f" % self._world.ball.bearing
        print "self._world.ball.dist: %f" % self._world.ball.dist
        
        print "midGoalBearing: %f" % midGoalBearing
        print "targetBearing: %f" % targetBearing
        print "targetDistance: %f" % targetBearing

        kpx = 0
        kpy = 0
        kpbearing = 0
        
        return kpx, kpy, kpbearing

    
    ##################### Computational Methods #########################
    
    def getTargetBearing(self):
        # TODO: Move to world data?
        # compute goal center bearing
        midGoalBearing = 0
        postsSeenCounter = 0
        if self._world.yglp.seen:
            print "self._world.yglp.bearing: %f" % self._world.yglp.bearing
            postsSeenCounter += 1
            midGoalBearing += self._world.yglp.bearing
        
        if self._world.ygrp.seen:
            print "self._world.ygrp.bearing: %f" % self._world.ygrp.bearing
            postsSeenCounter += 1
            midGoalBearing += self._world.ygrp.bearing
        
        if postsSeenCounter > 0:
            midGoalBearing = (self._world.yglp.bearing + self._world.ygrp.bearing)/postsSeenCounter
        print "midGoalBearing: %f" % midGoalBearing
        
        # determine if goal is left / right / center to ball
        bearingSum = self._world.ball.bearing + midGoalBearing
        bearingSumAbs = abs(self._world.ball.bearing) + abs(midGoalBearing)
        bearingProd = self._world.ball.bearing * midGoalBearing
        targetBearing = self._world.ball.bearing
        if bearingProd > 0:
            # ball and goal on same side
            if bearingSumAbs <  0.1745: # 10: --  bearing is radians (Vova)
                # ball and goal on same line (same sign, small sum)
                pass #targetBearing = self._world.ball.bearing
            else:
                # ball and goal on same side, far away (same sign, large sum)
                if abs(self._world.ball.bearing) > abs(midGoalBearing):
                    targetBearing *= 1.3
                else:
                    targetBearing *= 0.7
        else:
            # ball and goal on different sides
            if bearingSumAbs < 0.1745: # 10: --  bearing is radians (Vova)
                # ball and goal on roughly same line (different sign, small sum)
                if abs(self._world.ball.bearing) > abs(midGoalBearing):
                    targetBearing *= 1.2
                else:
                    targetBearing *= 0.8
            else:
                # ball and goal on same line (same sign, large sum)
                if abs(self._world.ball.bearing) > abs(midGoalBearing):
                    targetBearing *= 1.3
                else:
                    targetBearing *= 0.7

        #bearingOffset = (self._world.ball.bearing - midGoalBearing)/2.0
        #targetBearing = self._world.ball.bearing + bearingOffset * math.log(self._world.ball.dist - 33 + 1)/8.7
        
        print "self._world.ball.bearing: %f" % self._world.ball.bearing
        print "midGoalBearing: %f" % midGoalBearing
        print "targetBearing: %f" % targetBearing
        return targetBearing


if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Kicker).run()

