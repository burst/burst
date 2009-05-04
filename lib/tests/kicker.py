# TODO:
# Add slower walk when approaching ball (dynamic approach vs. static one)
# Align with goal for kick (need "around ball" movement), do camera switch for goal tracking? or use last goal position?
# Fix walk radius/arc issues
# Move consts somewhere nice
# Reality check

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

    def onTurnDone(self):
        print "Turn Done!"
        self._eventmanager.unregister(EVENT_TURN_DONE)
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
            
            # if we're walking and ball moves (bearing only, we ignore distance for now), stop
            # not working correctly, since it stops while we turn
            #if self._world.robot.isWalkingActive and abs(xNormalized) > 0.1:
            #    print "Ball moved, stopping to reassess"
            #    self._actions.sitPoseAndRelax()
            #    self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
            #    self._eventmanager.unregister(EVENT_WALK_DONE)
                     
        elif not self._world.robot.isWalkingActive and not self._world.robot.isTurningActive:
            #self._eventmanager.unregister(EVENT_BALL_IN_FRAME)
            print "self._world.ball.bearing: %f" % self._world.ball.bearing
            print "self._world.ball.dist: %f" % self._world.ball.dist
            
            if abs(self._world.ball.bearing) > 5:
                print "Starting to turn!"
                self._eventmanager.register(EVENT_TURN_DONE, self.onTurnDone)
                self._actions.turn(self._world.ball.bearing * DEG_TO_RAD)
            elif self._world.ball.dist > 35:
                print "Starting to walk!"
                self._eventmanager.register(EVENT_WALK_DONE, self.onWalkDone)
                self._actions.changeLocation(self._world.ball.dist - 35, 0, 0) # 30 = ball radius, update and re-position
            else:
                self._actions.kick()
                self._actions.sitPoseAndRelax()
                self._eventmanager.unregister(EVENT_BALL_IN_FRAME)


if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Kicker).run()

