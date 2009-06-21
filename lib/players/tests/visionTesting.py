#!/usr/bin/python
import os
from math import cos, sin
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.behavior import InitialBehavior
from burst_events import EVENT_BALL_IN_FRAME
import burst.moves as moves
from burst_util import polar2cart

class visionTesting(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.initPos()

    def initPos(self):
        self._actions.executeMove(moves.SIT_POS)
        self._eventmanager.register(self.printBall, EVENT_BALL_IN_FRAME)
    
    def printBall(self):
        ball_x = self._world.ball.dist * cos(self._world.ball.bearing)
        ball_y = self._world.ball.dist * sin(self._world.ball.bearing)
        print ball_x," , ", ball_y
        
if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(visionTesting).run()

