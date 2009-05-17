#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player
from burst.events import *
from burst.consts import *
from burst.eventmanager import AndEvent, SerialEvent

def pr(s):
    print s

class Template(Player):
    
    def onStart(self):
        if hasattr(self._world, '_shm'):
            self._eventmanager.register(EVENT_STEP, self.onStep)
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        self._eventmanager.setTimeoutEventParams(2.0, oneshot=True, cb=self.onTimeout)

    def onStep(self):
        print "donothing: ball dist is %s" % self._world.ball.dist

    def onTimeout(self):
        print "timed out at t = %s" % self._world.time
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Template).run()

