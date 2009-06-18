#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player

class HeadAndWalkTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness(None).onDone(lambda: self._actions.moveHead(-0.5,0.0)).onDone(self.start)

    def start(self):
        # Down, Left, Up, Right - learn your directions!
        self._eventmanager.callLater(3.5, self.moveHead)
        self._actions.changeLocationRelative(50.0, 0.0, 0.0)

    def moveHead(self):
        self._actions.moveHead(0.5,0.0).onDone(self._eventmanager.quit) 

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(HeadAndWalkTester).run()

