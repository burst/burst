#!/usr/bin/python

import player_init

from burst.player import Player
from burst.events import EVENT_BALL_IN_FRAME
import burst.moves as moves
from burst_util import polar2cart

class trackerTester(Player):
    
    def onStart(self):
        self.count = 1
        self._actions.setCameraFrameRate(20)
        self._actions.initPoseAndStiffness().onDone(self.initHeadPosition)
    
    def initHeadPosition(self):
        self._eventmanager.register(self.printBall, EVENT_BALL_IN_FRAME)
        self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_FAR).onDone(self.track)
    
    def track(self):
        print "trackerTester: TRACKING %s" % (self.count)
        self.count += 1
        self._actions.tracker.track(self._world.ball, lostCallback=self.trackNextFrame)

    def trackNextFrame(self):
        self._eventmanager.callLater(0.0, self.track)

    def wrapUp(self):
        print "tracker lost the ball"
        self._eventmanager.quit()
        
    def printBall(self):
        print "Ball seen!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
        print "Ball x: %3.3f, Ball y: %3.3f" % (ball_x, ball_y)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(trackerTester).run()

