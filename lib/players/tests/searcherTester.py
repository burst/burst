#!/usr/bin/python

import player_init
from burst.player import Player
import burst.events as events
from burst.actions.headtracker import Searcher

class SearchTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self.targets=[self._world.yglp, self._world.ygrp]
        self._actions.searcher.search(self.targets).onDone(self.onFound)

    def onFound(self):
        self._actions.say('Found it!')
        
        for t in self.targets:
            if t.centered_self.sighted_centered:
                print "%s sighted centered" % t.name
            else:
                print "%s NOT sighted centered" % t.name
        
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(SearchTester).run()

