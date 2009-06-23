#!/usr/bin/python

from math import pi

import player_init

from burst.behavior import InitialBehavior
import burst.field as field
from burst.actions.approacher import TurtleTurn, ApproachXYHActiveLocalization

class ApproachTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.log("Starting")
        #TurtleTurn( self._actions, 20.0, 0.0, pi/4, 2).start().onDone(self._onApproacherDone)
        ApproachXYHActiveLocalization(
            self._actions, field.MIDFIELD_X, field.MIDFIELD_Y, 0.0).start().onDone(self._onApproacherDone)

    def _onApproacherDone(self):
        self.log("Done")
        self.stop()
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(ApproachTester).run()

