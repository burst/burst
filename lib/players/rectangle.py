#!/usr/bin/python

import player_init

from math import pi, sqrt
import os

from burst.player import Player
from burst.events import *
from burst_consts import *
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
                    x, y, t, walk=moves.STRAIGHT_WALK, steps_before_full_stop=2)

        self._actions.initPoseAndStiffness()
        
        clr(0.0, side, pi).onDone(
            lambda: clr(side, 0, pi/2)).onDone(
            lambda: clr(side, 0, pi/4)).onDone(
            lambda: clr(side/sqrt(2), side/sqrt(2), pi/4)).onDone(
            self._eventmanager.quit
            )

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Rectangle).run()

