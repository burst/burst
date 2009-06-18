#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player

class Nod(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness(None).onDone(self.doNod)
    
    def doNod(self):
        print "Will Nod"
        # Down, Left, Up, Right - learn your directions!
        nods = [(0.0, 0.0), (0.0, 0.5), (0.0, 0.0), (0.5, 0.0),
            (0.0, 0.0), (0.0, -0.5), (0.0, 0.0), (-0.5, 0.0),
            (0.0, 0.0)]
        self._actions.chainHeads(nods).onDone(self._eventmanager.quit)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Nod).run()

