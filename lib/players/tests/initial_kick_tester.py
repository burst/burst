#!/usr/bin/python

from math import pi

import player_init

from burst.behavior import InitialBehavior
import burst.field as field
from burst.actions.initial_kicker import InitialKickWithSideKick
from burst_consts import (LEFT, RIGHT)

class InitialKickTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.log("Starting")
        InitialKickWithSideKick(self._actions, LEFT).start().onDone(self._onSideKickMade)


    def _onSideKickMade(self):
        self.log("Done")
        self.stop()
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(InitialKickTester).run()

