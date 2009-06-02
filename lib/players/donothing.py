#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.player import Player
from burst.events import *
from burst.consts import *
from burst.eventmanager import AndEvent, SerialEvent

def pr(s):
    print s

class Donothing(Player):
    
    def onStart(self):
        self._eventmanager.register(EVENT_STEP, self.onStep)
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        self._actions.initPoseAndStiffness().onDone(self.startWaiting)
        self._max = 10
        self._count = 0

    def startWaiting(self):
        print "doNothing: Starting to wait"
        #self._eventmanager.callLater(2.0, self.onTimeout)
        import pdb; pdb.set_trace()

    def onStep(self):
        self._count += 1
        if self._count < self._max: return
        self._count = 0
        print "donothing: ball dist is %s" % self._world.ball.dist
        print "donothing: top_yellow dist is %s" % self._world.ygrp.dist
        print "donothing: bottom_yellow dist is %s" % self._world.yglp.dist

    def onTimeout(self):
        print "timed out at t = %s" % self._world.time
        self._eventmanager.unregister(EVENT_STEP)
        self._actions.sitPoseAndRelax().onDone(self.onQuit)

    def onQuit(self):
        print "doNothing: quiting"
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Donothing).run()

