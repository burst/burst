#!/usr/bin/python

from math import pi, sqrt

from datetime import datetime
import os
import sys

in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *
from burst.consts import *
from burst.eventmanager import AndEvent, SerialEvent
import burst.moves as moves

def pr(s):
    print s

def debugme():
    import pdb; pdb.set_trace()

class Rectangle(Player):
    
    def onStart(self):

        now = datetime.now()
        self._world.startRecordAll('walk_%04d%02d%02d_%02d%02d%02d' % (
            now.year, now.month, now.day, now.hour, now.minute, now.second))
        self._actions.initPoseAndStiffness()
        self._actions.changeLocationRelative(
                    200.0, 0.0, 0.0, walk_param=moves.SLOW_WALK).onDone(
                      self.stopRecord)

    def stopRecord(self):
        print "done - stopping recording"
        self._world.stopRecord()
        self._actions.sitPoseAndRelax()
        self._eventmanager.quit()

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Rectangle).run()

