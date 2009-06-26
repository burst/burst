#!/usr/bin/python

import player_init
import burst
from burst.behavior import InitialBehavior


class Empty(InitialBehavior):
    def __init__(self, actions):
        super(Empty, self).__init__(actions=actions, name=self.__class__.__name__)
    def _start(self, firstTime):
        self._eventmanager.callLater(0.0, self.stop)


if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(Empty)
    mainloop.run()
