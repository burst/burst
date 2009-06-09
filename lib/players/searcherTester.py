#!/usr/bin/python

import player_init
from burst.player import Player
import burst.events as events
from burst.actions.headtracker import Searcher

class SearchTimeoutTester(Player):
    
    def onStart(self):
#        self._actions.initPoseAndStiffness()
        self._actions.searcher.search(targets=[self._world.yglp, self._world.ygrp, self._world.ball]).onDone(self.onFound)

    def onFound(self):
        self._actions.say('Found it!')
        self._eventmanager.quit()

    def onTimeout(self):
        print 'Couldn\'t find it!'
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(SearchTimeoutTester).run()

