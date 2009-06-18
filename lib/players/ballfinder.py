#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.player import Player
from burst.actions.target_finder import TargetFinder

class BallFinder(Player):
    
    def onStart(self):
        self._ballFinder = TargetFinder(actions=self._actions, targets=[self._world.ball], start=False)
        self._actions.initPoseAndStiffness(None
            ).onDone(self._ballFinder.start)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(BallFinder).run()
