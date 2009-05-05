#!/usr/bin/python

import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/tests')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *
from burst.consts import *

def pr(s):
    print s

class Goalie(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        self._eventmanager.register(EVENT_KP_CHANGED, self.onKickPointViable)
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        self._eventmanager.register(EVENT_BALL_BODY_X_ISECT_UPDATE, self.onBallApproachingMaybe)
        
        self._eventmanager.register(EVENT_ALL_BLUE_GOAL_SEEN, lambda: pr("Blue goal seen"))
        self._eventmanager.register(EVENT_ALL_YELLOW_GOAL_SEEN, lambda: pr("Yellow goal seen"))
        
    def onStop(self):
        super(Goalie, self).onStop()

    def onKickPointViable(self):
        print "Kick point viable:", self._world.computed.kp

    def onBallSeen(self):
        print "Ball Seen!"
        print "Ball x: %f" % self._world.ball.centerX
        print "Ball y: %f" % self._world.ball.centerY

    def onBallInFrame(self):
        print "ball bearing, dist %3.3f %3.3f" % (self._world.ball.bearing, self._world.ball.dist)
    
    def onBallApproachingMaybe(self):
        import pdb; pdb.set_trace()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Goalie).run()

