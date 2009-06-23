#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior
from burst_events import EVENT_BALL_IN_FRAME
import burst.moves.poses as poses
from burst_util import polar2cart

class DiagonalTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._actions.setCameraFrameRate(20)
        self._actions.executeHeadMove(poses.HEAD_MOVE_FRONT_FAR).onDone(self.find_goal)
    
    def find_goal(self):
        self._actions.localize().onDone(self.foundGoal)

    def foundGoal(self):
        yglp, ygrp = self._world.yglp, self._world.ygrp
        t = self._world.time
        dtl, dtr = t - yglp.update_time, t - ygrp.update_time
        print "Goal Posts Bearings: %3.2f, %3.2f (seens %s, %s), (updated %3.2f seconds ago)" % (
                yglp.bearing, ygrp.bearing, yglp.seen, ygrp.seen, max(dtl, dtr))
        self._eventmanager.callLater(1.0, self.track)
        #self._eventmanager.register(self.printBall, EVENT_BALL_IN_FRAME)

    def track(self):
        def callTrackLater():
            self._eventmanager.callLater(0.0, self.track)
        self._actions.tracker.track(self._world.ball, lostCallback=callTrackLater)

    def printBall(self):

        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
# minimal printing for spreadshit
#        print "%s, %3.3f, %3.3f, %3.3f, %3.3f, %3.3f" % (self._world.ball.seen, self._world.ball.dist,              self._world.ball.distSmoothed, self._world.ball.bearing, ball_x, ball_y)
# legible printing
        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)        
        print "dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f, Ball x: %3.3f, Ball y: %3.3f" % 	(self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing, ball_x, ball_y)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(DiagonalTester).run()

