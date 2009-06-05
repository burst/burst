#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_util import nicefloats

from burst.player import Player
from burst.events import *
from burst_consts import *

class Localize(Player):
    
    """ To be converted into an action:
    Search for both yellow gate posts, centering on each.
    Location will be computed by Localization once both posts
    are centered.

    TODO: To Be Called: LocalizeByFindingGate
    """

    def onStart(self):
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        self._actions.search([self._world.yglp, self._world.ygrp]).onDone(
            self.onSearchResults)
        
    def onSearchResults(self):
        robot = self._world.robot
        world_pos = (robot.world_x, robot.world_y, robot.world_heading)
        dists = tuple(nicefloats([x.my_dist, x.dist, x.focDist])
                    for x in self._world.team.target_posts.bottom_top)
        if not all(isinstance(x, float) for x in world_pos):
            print "ERROR: world position not computed. It is %r. dists are %s" % (world_pos, dists)
        else:
            print "position = %3.3f %3.3f %3.3f, dists %s" % (
                robot.world_x, robot.world_y, robot.world_heading, dists)
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Localize).run()

