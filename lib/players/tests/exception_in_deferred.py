#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

from burst_util import Deferred

class ExceptionInDeferred(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _throw(self):
        return 1/0

    def _start(self, firstTime=False):
        self._eventmanager.callLater(0.1, self._throw)
        Deferred(None).addCallback(self._throw2)

    def _throw2(self, _):
        return _ - 10

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(ExceptionInDeferred).run()

