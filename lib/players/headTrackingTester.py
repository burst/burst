#!/usr/bin/python
import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import EVENT_BALL_IN_FRAME

class headTrackingTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.trackBall)
    
    def trackBall(self):
        self._actions.executeTracking(self._world.ball)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(headTrackingTester).run()

