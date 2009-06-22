#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.behavior import InitialBehavior

class StartStopTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(StartStopTester).run()

