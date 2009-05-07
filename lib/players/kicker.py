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
import burst.moves as moves

import time

"""
Logic for Kicker:

search for ball in current frame
found ball -> center on ball
ball centered -> pitch up until goal is seen
goal is seen -> compute kp by hand (we have all three things - ball + both posts)
 -> gotoBall

alternatively, if KP_CHANGED is fired all registered cbs are cleared (unregister_all),
 proceed to gotoBall

gotoBall ->
 close enough to kick -> kick (not good right now - won't really hit ball)
 not close enough -> approach for kick (not implmeneted yet)
"""

class Kicker(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        self._eventmanager.register(EVENT_ALL_YELLOW_GOAL_SEEN, self.onGoalSeen)
        self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
        self.kp = None
        
    def onStop(self):
        super(Kicker, self).onStop()

    def onBallSeen(self):
        print "Ball Seen!"
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.centerOnBall)
        self._eventmanager.unregister(EVENT_BALL_SEEN)
        #print "Ball x: %f" % self._world.ball.centerX
        #print "Ball y: %f" % self._world.ball.centerY

        #test()

    def onKickingPointChanged(self):
        """ We can reach here either:
        via the EVENT_KP_CHANGED
        via pitchUpToFindGoal
        hence we actually look at the kp_valid parameter (otherwise
        we already set the kp before in pitchUpToFindGoal)
        """
        self._eventmanager.unregister_all()
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.doBallTracking)
        computed = self._world.computed
        if computed.kp_valid:
            self.kp = computed.kp
        if self.kp is None:
            print "Oops, kp not set - please debug me!"
            raise SystemExit
        print "KP: %3.3f, %3.3f, %3.3f" % self.kp
        print "self._world.ball.bearing: %f" % self._world.ball.bearing
        print "self._world.ball.dist: %f" % self._world.ball.dist
        
        self.gotoBall()
        
    def centerOnBall(self):
        """ look for a ball, when we have it move on to find the posts. no moving
        the robot, just the head """
        ball_frame_x = self.ball_frame_x()
        if (self._world.yglp.dist == 0.0 or self._world.ygrp.dist == 0.0
                and abs(ball_frame_x) < 0.05):
            self._eventmanager.register(EVENT_BALL_IN_FRAME, self.pitchUpToFindGoal)
        else:
            self.doBallTracking()
#        if self._world.robot.isMotionInProgress():
#            # robot is still walking / turning, return without doing anything
#            print "is walking: %f is turning: %f" % (self._world.robot.isWalkingActive, self._world.robot.isTurningActive)
#            return

    def pitchUpToFindGoal(self):
        if not self._world.yglp.dist > 0.0 or not self._world.yglp.dist > 0.0:
            # haven't seen either yglp or ygrp yet, move head up to find them.
            print "pitch up to find goal"
            self._actions.changeHeadAngles(0, -0.05)
        else:
            print "so we have goal, even if not both posts at the same time - compute kp using best values"
            self.kp = self._world.computed.calculate_kp()
            print "kp = (%3.3f, %3.3f, %3.3f)" % self.kp
            self.onKickingPointChanged()

    def onKickPointViable(self):
        print "Kick point viable:", self._world.computed.kp
        self._actions.kick()
        self._actions.sitPoseAndRelax()
       
    def onChangeLocationDone(self):
        print "Change Location Done!"
        self._eventmanager.unregister(EVENT_CHANGE_LOCATION_DONE)
        if abs(self._world.ball.bearing) <= 0.1745 and self._world.ball.dist <= 20:
            self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
            self.onKickPointViable()
        else:
            print "we are still too far to kick the ball, advance towards ball again"
            self._eventmanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
            #self.test()

        #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)

    def doBallTracking(self):
        xNormalized = self.ball_frame_x()
        yNormalized = self.ball_frame_y()
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

    def gotoBall(self):
        print "goto ball and kick"
        # ball is away, first turn and then approach ball
        delta_y, delta_x, delta_bearing = self.kp # TODO: fix x,y issues
        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        self._actions.changeLocationRelative(delta_x, delta_y, delta_bearing,
            walk_param = moves.KICKER_WALK)


    ##################### Debug Methods #########################

    def test(self):
        if self._world.robot.isHeadMotionInProgress():
            return
        
        self.kp = self.estimateKPwithoutGoal()
        
        print "KP: %3.3f, %3.3f, %3.3f" % self.kp
        print "self._world.ball.bearing: %f" % self._world.ball.bearing
        print "self._world.ball.dist: %f" % self._world.ball.dist
        
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
        print "targetDistance: %f" % targetDistance

        kpx = 0
        kpy = 0
        kpbearing = 0
        
        return kpx, kpy, kpbearing

    
    ##################### Computational Methods #########################
   
    def ball_frame_x(self):
        return (IMAGE_HALF_WIDTH - self._world.ball.centerX) / IMAGE_HALF_WIDTH # between 1 (left) to -1 (right)

    def ball_frame_y(self):
        return (IMAGE_HALF_WIDTH - self._world.ball.centerX) / IMAGE_HALF_WIDTH # between 1 (left) to -1 (right)
 
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

