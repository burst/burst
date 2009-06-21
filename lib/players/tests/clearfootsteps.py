#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class Clearfootsteps(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    # TODO
    def _start(self, firstTime=False):
        self.test()

    def test(self):
        self._actions.changeLocationRelative(500.0, 0.0, 0.0)
        self._eventmanager.callLater(2.0, self._actions.clearFootsteps)

    def cancelWalk(self):
        self._actions.cancelWalk()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Clearfootsteps).run()

