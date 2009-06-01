#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_util import Deferred, DeferredList

from burst.player import Player
from burst.events import *
from burst.consts import *
from burst.eventmanager import AndEvent, SerialEvent

import burst.kinematics as kinematics
from burst.kinematics import IMAGE_CENTER_X
from burst.field import (GOAL_POST_CM_HEIGHT, CROSSBAR_CM_WIDTH, yellow_goal,
    CROSSBAR_CM_WIDTH)

class Localize(Player):
    
    """ To be converted into an action:
    Search for both yellow gates, centering on each.
    Use results to compute location.

    TODO: To Be Called: LocalizeByFindingGate
    """

    def onError(self, result):
        if self._all_data_in.result is None:
            print "TODO - deferred threw exception, but the error object wasn't stored in result"
        else:
            print self._all_data_in.result.getTraceback()

    def onStart(self):
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        self._pose = kinematics.pose
        self._actions.search([self._world.yglp, self._world.ygrp]).onDone(
            self.onAvailableInformationForLocationCalculation)

        #for f in [self.onYellowBottomPosChange, self.onYellowTopPosChange]:
        #    self._eventmanager.register(f.event, f)

        self.registerDecoratedEventHandlers()
        
    @eventhandler(EVENT_YGRP_POSITION_CHANGED)
    def onYellowTopPosChange(self):
        obj = self._world.ygrp # Yellow Right is Top - since it's goalie looks towards minus x
        if obj.x == 0.0: return
        dx = abs(obj.x - IMAGE_CENTER_X)
        print "yellow top    - dx = %5s, x = %5s" % (dx, obj.x)
        if dx < MAX_PIXELS_FROM_CENTER_FOR_DISTANCE_ESTIMATE:
            print "yellow TOP DONE"
            self.yellow_top_dist = self._pose.pixHeightToDistance(obj.height, GOAL_POST_CM_HEIGHT)
            self.yellow_top_bearing = obj.bearing
            self._yellowtop.callback(None)
            self._eventmanager.unregister(self.onYellowTopPosChange.event)

    @eventhandler(EVENT_YGLP_POSITION_CHANGED)
    def onYellowBottomPosChange(self):
        obj = self._world.yglp # Yellow Left is Bottom - since it's goalie looks towards minus x
        if obj.x == 0.0: return
        dx = abs(obj.x - IMAGE_CENTER_X)
        print "yellow bottom - dx = %5s, x = %5s" % (dx, obj.x)
        if abs(obj.x - IMAGE_CENTER_X) < MAX_PIXELS_FROM_CENTER_FOR_DISTANCE_ESTIMATE:
            print "yellow BOTTOM DONE"
            self.yellow_bottom_dist = self._pose.pixHeightToDistance(obj.height, GOAL_POST_CM_HEIGHT)
            self._yellowbottom.callback(None)
            self._eventmanager.unregister(self.onYellowBottomPosChange.event)

    def onAvailableInformationForLocationCalculation(self, result):
        print "calculating position"
        d = CROSSBAR_CM_WIDTH / 2.0
        p0 = yellow_goal.top_post.xy
        p1 = yellow_goal.bottom_post.xy
        r1, r2, a1 = (self.yellow_top_dist, self.yellow_bottom_dist,
            self.yellow_top_bearing)
        if abs(r1 - r2) > 2*d:
            print "inputs are bad, need to recalculate"
            # This is fun: which value do I throw away? I could start collecting a bunch first,
            # and only if it is well localized (looks like a nice normal distribution) I use
            # it..
            self.
        x, y, theta = self._pose.xyt_from_two_dist_one_angle(
            r1=r1, r2=r2, a1=a1, d=d, p0=p0, p1=p1)
        print "GOT %3.3f %3.3f heading %3.3f deg" % (x, y, theta*RAD_TO_DEG)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Localize).run()

