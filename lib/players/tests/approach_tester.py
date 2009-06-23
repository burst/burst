#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

import burst.field as field

from burst.actions.approacher import ApproachXYActiveLocalization

class ApproachTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.log("Starting")
        ApproachXYActiveLocalization(self._actions, field.CENTER_FIELD_X+100, field.CENTER_FIELD_Y).start().onDone(self._onApproacherDone)

    def _onApproacherDone(self):
        self.log("Done")
        self.stop()
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(ApproachTester).run()

