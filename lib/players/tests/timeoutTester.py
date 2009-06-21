#!/usr/bin/python


import player_init
from burst.player import Player

class TimeoutTester(Player):
    
    def onStart(self):
        print "Hey!"
        self.searcher = self._actions.searcher
        self.searcher.search([self._world.ball], True, 10, self.onTimeout).onDone(self.onFound)

    def onFound(self):
        print 'Found it!'
        self._eventmanager.quit()

    def onTimeout(self):
        print "Couldn't find it!"
        self._eventmanager.quit()



if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(TimeoutTester).run()
