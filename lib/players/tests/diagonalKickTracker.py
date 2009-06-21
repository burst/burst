#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior
from burst.events import EVENT_BALL_IN_FRAME
import burst.moves.poses as poses
from burst_util import polar2cart

class trackerTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.count = 1
        self._actions.setCameraFrameRate(20)
        self._eventmanager.register(self.printBall, EVENT_BALL_IN_FRAME)
        self._actions.executeHeadMove(poses.HEAD_MOVE_FRONT_FAR).onDone(self.track)
    
    def track(self):
        #print "trackerTester: TRACKING %s" % (self.count)
        self.count += 1
        self._actions.tracker.track(self._world.ball, lostCallback=self.trackNextFrame)

    def trackNextFrame(self):
        self._eventmanager.callLater(0.0, self.track)

    def wrapUp(self):
        print "tracker lost the ball"
        self._eventmanager.quit()
        
    def printBall(self):

        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
# minimal printing for spreadshit
        print "%s, %3.3f, %3.3f, %3.3f, %3.3f, %3.3f" % (self._world.ball.seen, self._world.ball.dist,              self._world.ball.distSmoothed, self._world.ball.bearing, ball_x, ball_y)
# legible printing
#        print "Ball seen!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
#        print "Ball x: %3.3f, Ball y: %3.3f" % (ball_x, ball_y)


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(trackerTester).run()

