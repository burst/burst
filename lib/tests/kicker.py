import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/tests')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *

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

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Kicker).run()

