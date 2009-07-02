#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class TestQuitOnMainBehaviorStop(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.callLater(0.5, self.tryToStopMainBehavior)

    def tryToStopMainBehavior(self):
        print "stopping myself minchouzen style"
        self._eventmanager._mainloop._player._stopMainBehavior()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(TestQuitOnMainBehaviorStop).run()

