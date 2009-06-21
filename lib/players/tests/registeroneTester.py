#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.behavior import InitialBehavior
from burst.events import EVENT_STEP

class RegisterOneShotTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.count = 0
        self._eventmanager.register_oneshot(self.onStep, EVENT_STEP)
        self._eventmanager.register_oneshot(self.onStep10, EVENT_STEP)
        self._eventmanager.register(self.onStep100, EVENT_STEP)

    def onStep10(self):
        self.count += 10
        print "step 10:  count = %s" % self.count

    def onStep100(self):
        self.count += 100
        if self.count > 50:
            self._eventmanager.unregister(self.onStep100, EVENT_STEP)
        print "step 100: count = %s" % self.count

    def onStep(self):
        self.count += 1
        print "step:     count = %s" % self.count
        self._eventmanager.callLater(2.0, self._eventmanager.quit)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(RegisterOneShotTester).run()

