#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player

class HeadAndWalkTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness(None).onDone(self.start)

    def start(self):
        # Down, Left, Up, Right - learn your directions!
        nods = [(0.0, 0.0), (0.0, 0.5), (0.0, 0.0), (0.5, 0.0),
            (0.0, 0.0), (0.0, -0.5), (0.0, 0.0), (-0.5, 0.0),
            (0.0, 0.0)]
        self._actions.chainHeads(nods).onDone(self._eventmanager.quit)
        self._actions.changeLocationRelative(50.0, 0.0, 0.0)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(HeadAndWalkTester).run()

