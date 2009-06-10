#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player

class StartStopTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness().onDone(self._eventmanager.quit)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(StartStopTester).run()

