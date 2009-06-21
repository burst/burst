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

from burst.behavior import InitialBehavior
from burst.events import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent
import burst.moves as moves

def pr(s):
    print s

def debugme():
    import pdb; pdb.set_trace()

class Rectangle(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        open('varnames.txt', 'w+').write('\n'.join(self._world.getRecorderVariableNames()))
        self._eventmanager.quit()

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Rectangle).run()

