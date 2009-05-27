#!/usr/bin/python
import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import EVENT_BALL_IN_FRAME
import burst.moves as moves
from burst_util import polar2cart

class headTrackingTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self._actions.executeSyncHeadMove(moves.HEAD_MOVE_FRONT_BOTTOM)
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.trackBall)
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

