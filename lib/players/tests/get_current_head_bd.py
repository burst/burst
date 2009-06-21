#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class GetCurrentHeadBD(InitialBehavior):

    # TODO - or use nodtester
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.moveit()

    def moveit(self):
        self._actions.changeLocationRelative(500.0, 0.0, 0.0)
        self._eventmanager.callLater(2.0, self.cancelWalk)

    def cancelWalk(self):
        self._actions.cancelWalk()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(GetCurrentHeadBD).run()

