#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player
from burst.events import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent

def pr(s):
    print s

class CallLaterTester(Player):
    
    def onStart(self):
        self._eventmanager.callLater(EVENT_MANAGER_DT, self.onQuit)

    def onQuit(self):
        print "CallLaterTester: called"
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(CallLaterTester).run()

