#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class QuittingBehavior(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.callLater(1.0, self.stop)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(QuittingBehavior).run()

