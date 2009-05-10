#!/usr/bin/python

from math import pi

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

def pr(s):
    print s

BEARING_THRESHOLD = 0.15
BASE_BEARING = -1.50 # TODO


class EladGoalie(Player):
    
    def onStart(self):
#        self._actions.initPoseAndStiffness()
        self._world.robot._motion.setBodyStiffness(1.0)
        self._headX, self._headY = -90*DEG_TO_RAD, -20*DEG_TO_RAD
        self._actions.getToGoalieInitPosition()
#        self._eventmanager.register(EVENT_BALL_LOST, self.searchForBall)
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.getInFrontOfBall)


    def onStop(self):
        self._actions.clearFootsteps()


    def searchForBall(self):
        pass


    def trackBall(self):
        pass        


    def getInFrontOfBall(self):
        if self._world.ball.bearing > BASE_BEARING + BEARING_THRESHOLD: # TODO: Make sure this works well for close as well as far balls.
            self._actions.blockingStraightWalk(0.05)
        elif self._world.ball.bearing < BASE_BEARING - BEARING_THRESHOLD:
            self._actions.blockingStraightWalk(-0.05)


if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(EladGoalie).run()

