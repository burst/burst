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
        self._actions.say('Found it!')
        
    def onTargetLost(self):
        self._actions.say('Lost it!')

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(TargetFinderTester).run()

