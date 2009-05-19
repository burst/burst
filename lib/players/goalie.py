#!/usr/bin/python
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
import burst.moves as moves
from math import cos, sin
import time

class goalie(Player):
    
#    def onStop(self):
#        super(Goalie, self).onStop()

    def onStart(self):
        self.kp = None

        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)        
        self._actions.initPoseAndStiffness()
        self._actions.executeHeadMove( (((70,50 ),0.15),) )
        #self._actions.executeLeapLeft()
        #self._actions.executeLeapRight()
        self.walkStartTime = time.time()
        #self.test()

    def test(self):
        self._actions.changeLocationRelative(100.0)
#        self._actions.executeSyncMove(moves.GREAT_KICK_RIGHT)
#        self._actions.executeSyncMove(moves.GREAT_KICK_LEFT)
#        self._actions.sitPoseAndRelax()
#        self._eventmanager.quit()
    
    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - tool approximately %f" % (self.walkEndTime - self.walkStartTime)
        #self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(goalie).run()

