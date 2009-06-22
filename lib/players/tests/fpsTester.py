#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst.actions.target_finder import TargetFinder

class FPSTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.targets=[self._world.ball]

        self._actions.setCameraFrameRate(20)

        self._ballFinder = TargetFinder(actions=self._actions, targets=self.targets, start=True)
        self._ballFinder.setOnTargetFoundCB(self.onTargetFound)
        self._ballFinder.setOnTargetLostCB(self.onTargetLost)

    def onTargetFound(self):
        self.log('Found it (changing to FPS 1)')
        self._actions.setCameraFrameRate(1)

    def onTargetLost(self):
        self.log('Lost it (changing to FPS 20)')
        self._actions.setCameraFrameRate(20)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(FPSTester).run()

