#!/usr/bin/python

# DON'T PUT ANYTHING BEFORE THIS LINE
import player_init

from burst.player import Player
from burst.consts import *
import burst.moves as moves
from math import cos, sin
import time

class walkTester(Player):
    
#    def onStop(self):
#        super(Kicker, self).onStop()

    def onStart(self):
        self.kp = None
        self._actions.initPoseAndStiffness().onDone(self.initKickerPosition)
        
    def initKickerPosition(self):
        self._actions.executeMoveRadians(moves.STRAIGHT_WALK_INITIAL_POSE).onDone(self.testWalk)

    def testWalk(self):
        self.walkStartTime = time.time()
        self._actions.changeLocationRelative(30.0, 0.0, 0.0).onDone(self.onWalkDone)
#        self._actions.executeMove(moves.GREAT_KICK_RIGHT).onDone(
#           lambda: self._actions.executeMove(moves.GREAT_KICK_LEFT)).onDone(
#           lambda: self._actions.sitPoseAndRelax())
#        self._eventmanager.quit()
    
    def onWalkDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - tool approximately %f" % (self.walkEndTime - self.walkStartTime)
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(walkTester).run()

