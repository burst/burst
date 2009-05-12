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

class walkTester(Player):
    
#    def onStop(self):
#        super(Kicker, self).onStop()

    def onStart(self):
        self.kp = None

        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)        
        #self._actions.initPoseAndStiffness()
        self.walkStartTime = time.time()
        self.test()

    def test(self):
        self._actions.changeLocationRelative(100.0)
    
    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - tool approximately %f" % (self.walkEndTime - self.walkStartTime)
        #self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(walkTester).run()

