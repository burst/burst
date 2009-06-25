#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class centerTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        #target = self._world.opposing_goal.right
        target = self._world.ball
        self._actions.centerer.start(target=target, lostCallback=self.onLost).onDone(self.wrapUp)

    def onLost(self):
        self.log("lost ball")
        self._eventmanager.quit()

    def wrapUp(self):
        self.log("calling center again to make sure it works when already centered")
        self._actions.centerer.start(target=self._world.ball).onDone(self.reallyWrapUp)

    def reallyWrapUp(self):
        self.log("centered again!")
        self._eventmanager.quit()


if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(centerTester).run()

