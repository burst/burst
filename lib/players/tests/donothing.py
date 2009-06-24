#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent
import burst.moves.poses as poses

def pr(s):
    print s

class Donothing(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=None)

    def _start(self, firstTime=False):
        self._eventmanager.register(self.onStep, EVENT_STEP)
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        self._max = 10
        self._count = 0

    def startWaiting(self):
        print "doNothing: Starting to wait"
        self._eventmanager.callLater(20.0, self.onTimeout)

    def onStep(self):
        self._count += 1
        if self._count < self._max: return
        self._count = 0
        print "donothing: ball dist is %s" % self._world.ball.dist
        print "donothing: top_yellow dist is %s" % self._world.opposing_rp.dist
        print "donothing: bottom_yellow dist is %s" % self._world.opposing_lp.dist

    def onTimeout(self):
        print "timed out at t = %s" % self._world.time
        self._eventmanager.unregister(self.onStep)
        self._actions.sitPoseAndRelax().onDone(self.onQuit)

    def onQuit(self):
        print "doNothing: quiting"
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Donothing).run()

