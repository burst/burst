#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior
from burst.events import EVENT_BALL_IN_FRAME
import burst.moves as moves
from burst_util import polar2cart

class headTrackingTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_BOTTOM).onDone(
            lambda: self._eventmanager.register(self.trackBall, EVENT_BALL_IN_FRAME))
        self._last_ball_loc = (0.0, 0.0)
    
    def trackBall(self):
        new_ball_loc = self._world.ball.centerX, self._world.ball.centerY
        if new_ball_loc != self._last_ball_loc:
            print "ball at %s" % str(new_ball_loc)
            self._last_ball_loc = new_ball_loc
        self._actions.executeTracking(self._world.ball)
        
        print "Ball seen!: (ball seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (self._world.ball.seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)
        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
        print "Ball x: %3.3f, Ball y: %3.3f" % (ball_x, ball_y)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(headTrackingTester).run()

