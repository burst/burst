#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.behavior import InitialBehavior

class CallLaterTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.callLater(self._eventmanager.dt, self.onQuit)

    def onQuit(self):
        print "CallLaterTester: called"
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(CallLaterTester).run()

