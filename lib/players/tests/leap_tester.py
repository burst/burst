#!/usr/bin/python

# DON'T PUT ANYTHING BEFORE THIS LINE
import player_init

from burst.behavior import InitialBehavior
from burst_consts import *
from players.goalie import Goalie
import players.goalie as goalie
import burst.moves.walks as walks
import burst.moves.poses as poses

import time

class LeapTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._goalie = Goalie(self._actions)
        print goalie.realLeap
        print goalie.debugLeapRight
        goalie.realLeap = True
        goalie.debugLeapRight = True
        self._goalie.leapPenalty()
        #leap
                

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(LeapTester).run()
