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

class ShowPosts(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=None)

    def _start(self, firstTime=False):
        self._eventmanager.register(self.onStep, EVENT_STEP)
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        print "printing post locations, move the robot please"
        self._max = 10
        self._count = 0
        self.posts = list(self._world.opposing_goal.bottom_top) + list(self._world.our_goal.bottom_top)

    def onStep(self):
        self._count += 1
        if self._count < self._max: return
        self._count = 0
        self.log(' | '.join('%3.2f %3.2f %3.2f %3.2f %3.2f %3.2f' % (p.seen, p.update_time, p.bearing, p.dist, p.centerX, p.centerY) for p in self.posts))

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(ShowPosts).run()

