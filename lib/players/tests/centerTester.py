#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class centerTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        lambda: self._actions.tracker.center(self._world.ball, self.onLost).onDone(self.wrapUp)

    def onLost(self):
        print "lost ball"
        self._eventmanager.quit()

    def wrapUp(self):
        print "center done"
        print "calling center again to make sure it works when already centered"
        self._actions.tracker.center(self._world.ball).onDone(self.reallyWrapUp)

    def reallyWrapUp(self):
        print "centered again!"
        self._eventmanager.quit()


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(centerTester).run()

