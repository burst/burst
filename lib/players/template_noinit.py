#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class NoInit(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=None)

    def _start(self, firstTime=False):
        pass

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(NoInit).run()

