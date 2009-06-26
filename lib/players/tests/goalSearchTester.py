#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst.actions.searcher import Searcher

class SearchTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.targets=[self._world.opposing_lp, self._world.opposing_rp]
        self._actions.searcher.search(self.targets).onDone(self.onFound)

    def onFound(self):
        self._actions.say('Found it!')

        for t in self.targets:
            if t.centered_self.sighted_centered:
                print "%s sighted centered" % t.name
            else:
                print "%s NOT sighted centered" % t.name

        self.stop()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(SearchTester).run()

