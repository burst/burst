#!/usr/bin/python

# DON'T PUT ANYTHING BEFORE THIS LINE
import player_init

from burst.player import Player
from burst.events import *
from burst.consts import *
import burst.moves as moves
from math import cos, sin
import time

class walkTester(Player):
    
#    def onStop(self):
#        super(Kicker, self).onStop()

    def onStart(self):
        self.kp = None

        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)        
        self._actions.initPoseAndStiffness()
        self.walkStartTime = time.time()
        self.test()

    def test(self):
        self._actions.changeLocationRelative(100.0)
#        self._actions.executeMove(moves.GREAT_KICK_RIGHT).onDone(
#           lambda: self._actions.executeMove(moves.GREAT_KICK_LEFT)).onDone(
#           lambda: self._actions.sitPoseAndRelax())
#        self._eventmanager.quit()
    
    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - tool approximately %f" % (self.walkEndTime - self.walkStartTime)
        #self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(walkTester).run()

