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

BEARING_THRESHOLD = 0.05
BASE_BEARING = -1.50 # TODO


class EladGoalie(Player):
    
    def onStart(self):
        self._actions.getToGoalieInitPosition()
        self._headX, self._headY = -90*DEG_TO_RAD, -20*DEG_TO_RAD
        self._eventmanager.register(EVENT_BALL_LOST, self.searchForBall)
        self._eventmanager.register(EVENT_BALL_SEEN, self.trackBall)
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.getInFrontOfBall)

    """
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        
        self._eventmanager.register(EVENT_ALL_BLUE_GOAL_SEEN, lambda: pr("Blue goal seen"))
        self._eventmanager.register(EVENT_ALL_YELLOW_GOAL_SEEN, lambda: pr("Yellow goal seen"))
    """

    
    def onStop(self):
        self._actions.clearFootsteps()


    def searchForBall(self):
        pass


    def trackBall(self):
        pass        
        #if self.


    def getInFrontOfBall(self):
        print self._world.ball.bearing
        #self._actions.clearFootsteps()
        if self._world.robot.isMotionInProgress():
            raise SystemExit("WTF?!?!?!?!")
        if self._world.ball.bearing > BASE_BEARING + BEARING_THRESHOLD: # TODO: Make sure this works well for close as well as far balls.
            self._actions.blockingStraightWalk(0.15)
        elif self._world.ball.bearing < BASE_BEARING - BEARING_THRESHOLD:
            self._actions.blockingStraightWalk(-0.15)

    """
    def onBallSeen(self):
        print "Ball Seen! " + "Ball x: %f, " % self._world.ball.centerX + "y: %f" % self._world.ball.centerY
#        raise SystemExit # TODO

    def onBallInFrame(self):
        print "ball bearing, dist %3.3f %3.3f" % (self._world.ball.bearing, self._world.ball.dist)
    """

        

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(EladGoalie).run()

