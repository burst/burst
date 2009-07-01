#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst.actions.target_finder import TargetFinder

class TargetFinderTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        #self.targets=[self._world.opposing_lp, self._world.opposing_rp]
        self.targets=[self._world.ball]

        self._ballFinder = TargetFinder(actions=self._actions, targets=self.targets, start=True)
        self._ballFinder.setOnTargetFoundCB(self.onTargetFound)
        self._ballFinder.setOnTargetLostCB(self.onTargetLost)
        self._ballFinder.setOnSearchFailedCB(self.onSearchFailed)

    def onSearchFailed(self):
        self.log('Search Failed')
        self._ballFinder.stop().onDone(self.onStopped)

    def onTargetFound(self):
        self.log('Found it')
        self._actions.say('Found it!')
        self._ballFinder.stop().onDone(self.onStopped)

    def onTargetLost(self):
        self.log('Lost it')
        self._actions.say('Lost it!')

    def onStopped(self):
        self.log('Stopped')
        self._actions.say('Stopped')
        self._eventmanager.callLater(1.0, self._eventmanager.quit)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(TargetFinderTester).run()

