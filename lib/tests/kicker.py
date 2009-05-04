# TODO:
# Add world representation for robot? add "is walking" state (or is getRemainingFootStepCount enough?)
# Replace self.isWalkingTowardsBall with a robot model replacement?
# Add turn, walk according to distance
# Add slower walk when approaching ball
# Add movement around ball when near it (preparation for kick)
# Kick!
# Fix walk radius/arc issues

import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/tests')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *
from burst.consts import *

def pr(s):
    print s

class Kicker(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        #self._eventmanager.register(EVENT_ALL_BLUE_GOAL_SEEN, lambda: pr("Blue goal seen"))
        #self._eventmanager.register(EVENT_ALL_YELLOW_GOAL_SEEN, lambda: pr("Yellow goal seen"))
        
    def onStop(self):
        super(Kicker, self).onStop()

    def onBallSeen(self):
        print "Ball Seen!"
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        print "Ball x: %f" % self._world.ball.centerX
        print "Ball y: %f" % self._world.ball.centerY

    def onWalkDone(self):
        print "Walk Done!"
        self._eventmanager.unregister(EVENT_WALK_DONE)
        #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        
    def onBallInFrame(self):
        xNormalized = (IMAGE_HALF_WIDTH - self._world.ball.centerX) / IMAGE_HALF_WIDTH # between 1 (left) to -1 (right)
        yNormalized = (IMAGE_HALF_HEIGHT - self._world.ball.centerY) / IMAGE_HALF_HEIGHT # between 1 (up) to -1 (down)
        
        if abs(xNormalized) > 0.05 or abs(yNormalized) > 0.05:
            X_TO_RAD_FACTOR = 23.2/2 * DEG_TO_RAD #46.4/2
            Y_TO_RAD_FACTOR = 17.4/2 * DEG_TO_RAD #34.8/2
            
            deltaHeadYaw = xNormalized * X_TO_RAD_FACTOR
            deltaHeadPitch = -yNormalized * Y_TO_RAD_FACTOR
            #self._actions.changeHeadAngles(deltaHeadYaw * DEG_TO_RAD + self._actions.getAngle("HeadYaw"), deltaHeadPitch * DEG_TO_RAD + self._actions.getAngle("HeadPitch")) # yaw (left-right) / pitch (up-down)
            self._actions.changeHeadAngles(deltaHeadYaw, deltaHeadPitch) # yaw (left-right) / pitch (up-down)
        elif not self._world.isWalkingActive:
            #self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
            print "self._world.ball.bearing: %f" % self._world.ball.bearing
            print "self._world.ball.dist: %f" % self._world.ball.dist
            
            if abs(self._world.ball.bearing) > 5:
                print "Starting to turn!"
                self._eventmanager.register(EVENT_WALK_DONE, self.onWalkDone)
                self._actions.changeLocation(0, 0, self._world.ball.bearing * DEG_TO_RAD) #self._actions.getAngle("HeadYaw")
            elif self._world.ball.dist > 40:
                print "Starting to walk!"
                self._eventmanager.register(EVENT_WALK_DONE, self.onWalkDone)
                # TODO
                #if self._world.ball.dist > 40:
                    #fast walk
                #else:
                    #slow walk
                self._actions.changeLocation(self._world.ball.dist, 0, 0)
            else:
                self._actions.kick()
                self._actions.sitPoseAndRelax()
                self._eventmanager.unregister(EVENT_BALL_IN_FRAME)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Kicker).run()

