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

class Kicker(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        
    def onStop(self):
        super(Kicker, self).onStop()

    def onBallSeen(self):
        print "Ball Seen!"

    def onBallInFrame(self):
        print self._world.ball.centerX, self._world.ball.centerY
        print self._world.ball.bearing

        xtodeg = (IMAGE_HALF_WIDTH-self._world.ball.centerX)/IMAGE_HALF_WIDTH # between 1 (left) to -1 (right)
        print "xtodeg: %f" % xtodeg
        
        if (abs(xtodeg)>0.05):
            X_TO_DEG_FACTOR = 23.2/4 #46.4/2
            deltaHeadYaw = xtodeg*X_TO_DEG_FACTOR
            print "deltaHeadYaw: %f" % deltaHeadYaw
            self._actions.changeHeadAngles(deltaHeadYaw * DEG_TO_RAD, 0.0 * DEG_TO_RAD) # yaw (left-right) / pitch (up-down)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Kicker).run()

