#!/usr/bin/python

import player_init
from burst.player import Player
from burst.actions.target_finder import TargetFinder

class TargetFinderTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        #self.targets=[self._world.yglp, self._world.ygrp]
        self.targets=[self._world.ball]
        
        self._ballFinder = TargetFinder(actions=self._actions, targets=self.targets, start=True)
        self._ballFinder.setOnTargetFoundCB(self.onTargetFound)
        self._ballFinder.setOnTargetLostCB(self.onTargetLost)
        
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
