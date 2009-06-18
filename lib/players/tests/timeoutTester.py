#!/usr/bin/python


import player_init
from burst.player import Player
import burst.events as events


class Kicker(Player):
    
    def onStart(self):
        print "Hey!"
        self.tracker = self._actions.tracker
        self.searcher = self._actions.searcher
        self.searcher.search([self.obj], True, 10, self.onTimeout).onDone(self.onFound)

    def onFound(self):
        print 'Found it!'
        self._eventmanager.quit()

    def onTimeout(self):
        print "Couldn't find it!"
        self._eventmanager.quit()



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
