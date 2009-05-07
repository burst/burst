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
from burst.eventmanager import AndEvent, SerialEvent

def pr(s):
    print s

class Rectangle(Player):
    
    def onStart(self):

        # Serial event example: do one, then the other, call a cb on each
        #self._actions.turn(0.2)
        #self._actions.changeLocation(20, 0, 0)
        self.rect_i = 0
        # rectangle, meant to check actions.ChangeLocation
        # expected behavior: (in logo style)
        #  rt 90 fw 40 lt 90 fw 40 lt 90 fw 40 lt 45 lt 45 fw 40 rt 45 rt 135
        clr = self._actions.changeLocationRelative

        self._actions.initPoseAndStiffness().onDone(
            lambda: clr(0, 40, 0.0)).onDone(
            lambda: clr(40, 0, pi/2)).onDone(
            lambda: clr(40, 0, pi/4)).onDone(
            lambda: clr(40/sqrt(2), 40/sqrt(2), -3*pi/4)).onDone(
            lambda: pr('rectangle done')
            )

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Rectangle).run()

