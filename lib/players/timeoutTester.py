#!/usr/bin/python


import player_init
from burst.player import Player
import burst.events as events


class Kicker(Player):
    
    def onStart(self):
        print "Hey!"
        self._actions.searcher.search(targets=[self._world.ball],
            timeout=10, timeoutCallback=self.onTimeout).onDone(self.onFound)

    def onFound(self):
        print 'Found it! quitting in 20'
        self._eventmanager.callLater(20, self._eventmanager.quit)

    def onTimeout(self):
        print "Couldn't find it! quitting in 20"
        self._eventmanager.callLater(20, self._eventmanager.quit)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
