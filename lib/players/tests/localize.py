#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_util import nicefloats

from burst.player import Player
from burst.events import EVENT_WORLD_LOCATION_UPDATED
from burst_consts import *
from burst import moves

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
        #self._actions.initPoseAndStiffness(moves.SIT_POS).onDone(self._ook)
        self._ook()

    def _ook(self):
        self._eventmanager.register(self._worldLocationUpdated, EVENT_WORLD_LOCATION_UPDATED)
        self._actions.localize().onDone(self.doneLocalizing)
        
    def doneLocalizing(self):
        print "Localize: done localizing"
        self._worldLocationUpdated()

    def _worldLocationUpdated(self):
        robot = self._world.robot
        world_pos = (robot.world_x, robot.world_y, robot.world_heading)
        def get_my_dist(t):
            return (hasattr(t, 'my_dist') and t.my_dist) or -1e10
        dists = tuple(nicefloats([get_my_dist(x), x.dist, x.focDist])
                    for x in self._world.team.target_posts.bottom_top)
        if not all(isinstance(x, float) for x in world_pos):
            print "ERROR: world position not computed. It is %r. dists are %s" % (world_pos, dists)
        else:
            print "position = (x = %3.3f cm | y = %3.3f cm | th = %3.3f deg), dists %s" % (
                robot.world_x, robot.world_y, robot.world_heading * RAD_TO_DEG, dists)
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Localize).run()

