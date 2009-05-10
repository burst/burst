#!/usr/bin/python

from math import pi, sqrt

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
import burst.moves as moves

def pr(s):
    print s

class Rectangle(Player):
    
    def onStart(self):

        # rectangle, meant to check actions.ChangeLocation
        # expected behavior: (in logo style)
        #  lt 90 fw 40 rt 90 fw 40 rt 90 fw 40 rt 45 rt 45 fw 40 lt 45 lt 135

        #self._actions.initPoseAndStiffness().onDone(
        #    lambda: self._actions.initPoseAndStiffness()).onDone(
        #    lambda: pr('deferred chain test done')
        #    )
        #return

        #def first():
        #    return clr(side, 0.0)
        #
        #def second():
        #    return clr(0.0, 0.0, 0.1)
        #
        #bla = self._actions.initPoseAndStiffness().onDone(first).onDone(second)

        side = 40
        clr = lambda x, y, t: self._actions.changeLocationRelative(
                    x, y, t, walk_param=moves.KICKER_WALK)

        self._actions.initPoseAndStiffness()
        
        lambda: clr(0.0, side, pi).onDone(
            lambda: clr(side, 0, pi/2)).onDone(
            lambda: clr(side, 0, pi/4)).onDone(
            lambda: clr(side/sqrt(2), side/sqrt(2), pi/4)).onDone(
            lambda: pr('rectangle done')
            )

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Rectangle).run()

