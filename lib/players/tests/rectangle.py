#!/usr/bin/python

import player_init

from math import pi, sqrt
import os

from burst.behavior import InitialBehavior
from burst.events import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent
import burst.moves.walks as walks

def pr(s):
    print s

class Rectangle(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        # rectangle, meant to check actions.ChangeLocation
        # expected behavior: (in logo style)
        #  lt 90 fw 40 rt 90 fw 40 rt 90 fw 40 rt 45 rt 45 fw 40 lt 45 lt 135

        #def first():
        #    return clr(side, 0.0)
        #
        #def second():
        #    return clr(0.0, 0.0, 0.1)
        #
        #bla = first).onDone(second()

        side = 40
        clr = lambda x, y, t: self._actions.changeLocationRelative(
                    x, y, t, walk=walks.STRAIGHT_WALK, steps_before_full_stop=2)

        clr(0.0, side, pi).onDone(
            lambda: clr(side, 0, pi/2)).onDone(
            lambda: clr(side, 0, pi/4)).onDone(
            lambda: clr(side/sqrt(2), side/sqrt(2), pi/4)).onDone(
            self._eventmanager.quit
            )

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Rectangle).run()

