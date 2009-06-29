#!/usr/bin/python

import traceback
import sys

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_util import nicefloats

from burst.behavior import InitialBehavior
from burst_events import EVENT_WORLD_LOCATION_UPDATED, EVENT_STEP
from burst_consts import *
from burst import moves

class LocalizeTester(InitialBehavior):

    """ Test the localize action, which currently searches for the yellow gate.
    """

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.register(self._worldLocationUpdated, EVENT_WORLD_LOCATION_UPDATED)
        self._eventmanager.register(self._step, EVENT_STEP)
        self._actions.localize()

    def doneLocalizing(self):
        self.log("done localizing")
        self._worldLocationUpdated()

    last_time = 0.0
    def _step(self):
        if self._world.time < self.last_time + 0.2: return
        self.last_time = self._world.time
        for obj in list(self._world.opposing_goal.bottom_top) + \
                    list(self._world.our_goal.bottom_top):
            print obj.seen,
        print

    def _worldLocationUpdated(self):
        robot = self._world.robot
        world_pos = (robot.world_x, robot.world_y, robot.world_heading)
        def get_my_dist(t):
            return (hasattr(t, 'my_dist') and t.my_dist) or -1e10
        bottom_top = self._world.opposing_goal.bottom_top
        dists = tuple(nicefloats([get_my_dist(x), x.dist, x.focDist])
                    for x in bottom_top)
        bearings = nicefloats([x.bearing for x in bottom_top])
        if not all(isinstance(x, float) for x in world_pos):
            result = "ERROR: world position not computed. It is %r. dists are %s" % (world_pos, dists)
        else:
            result = "position = (x = %3.3f cm | y = %3.3f cm | th = %3.3f deg), dists %s" % (
                robot.world_x, robot.world_y, robot.world_heading * RAD_TO_DEG, dists)
        self.log('time = %3.2f; bearing: %s, %s' % (self._world.time,
                bearings, result))
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(LocalizeTester).run()

