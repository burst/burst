#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player

class CallLaterTester(Player):
    
    def onStart(self):
        self._eventmanager.callLater(self._eventmanager.dt, self.onQuit)

    def onQuit(self):
        print "CallLaterTester: called"
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(CallLaterTester).run()

