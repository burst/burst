#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior
import burst_events
import burst.moves as moves
from burst_util import polar2cart

class kickTuner(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.count = 1
        self._eventmanager.register(self.onBallInFrame, burst_events.EVENT_BALL_IN_FRAME)
        self.track()

    def track(self):
        print "kickTuner: TRACKING %s" % (self.count)
        self.count += 1
        self._actions.tracker.track(self._world.ball, lostCallback=self.trackNextFrame)

    def onBallInFrame(self):
        ball = self._world.ball
        if ball.seen:
            print "ball: centerX %s, centerY %s" % (ball.centerX, ball.centerY)
        print "Ball seen!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
        print "Ball x: %3.3f, Ball y: %3.3f" % (ball_x, ball_y)

    def trackNextFrame(self):
        self._eventmanager.callLater(0.0, self.track)

    def wrapUp(self):
        print "tracker lost the ball"
        self._eventmanager.quit()


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(kickTuner).run()

