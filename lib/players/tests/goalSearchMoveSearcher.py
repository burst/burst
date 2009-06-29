#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst.actions.searcher import Searcher
from burst_util import chainDeferreds


class SearchTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.targets=[self._world.opposing_lp, self._world.opposing_rp]
        self._startSearch()

    def _startSearch(self):
        self._actions.searcher.search(self.targets).onDone(self.onFound)

    def onFound(self):
        searcher = self._actions.searcher
        if not set(searcher.seen_objects) >= set(self.targets):
            print "Haven't Found it"
            if searcher.wantsToMove():
                self.log("searcher suggested move: %s" % searcher.wantedMove())
                move = searcher.wantedMove()
                if hasattr(move, '__len__'):
                    # location change
                    print "ERROR: goal search doesn't change location"
                    self._eventmanager.quit()
                else:
                    self.log("TURNING")
                    # turning
                    self._actions.turn(move).onDone(self._startSearch)
                    return
            else:
                self._eventmanager.quit()
        self.log('Found it!')

        self.log(' | '.join(map(str, self.targets)))

        for t in self.targets:
            if t.centered_self.sighted_centered:
                print "%s sighted centered" % t.name
            else:
                print "%s NOT sighted centered" % t.name

        if len([x for x in self.targets if x.centered_self.sighted]) == 0:
            print "Nothing found, not looking at targets"
            return self._quit()
        self.log("Going towards all targets")
        chainDeferreds([
            lambda _, t=t: self.lookAt(t).onDone(
            lambda: self._eventmanager.callLaterBD(2.0)).getDeferred()
                for t in self.targets]).addCallback(self._quit)

    def lookAt(self, target):
        self.log("Looking and centering on %s" % target.name)
        return self._actions.headTowards(target).onDone(
            lambda: self._actions.centerer.start(target=target))

    def _quit(self, _=None):
        self.stop()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(SearchTester).run()

