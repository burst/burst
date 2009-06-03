#!/usr/bin/python

import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent

def pr(s):
    print s

class Template(Player):
    
    def onStart(self):
        # uncomment this for real work - but for just getting events you probably want to keep it commented.
        self._actions.initPoseAndStiffness()
        self._eventmanager.register(EVENT_BALL_SEEN, self.onBallSeen)
        #self._eventmanager.register(EVENT_KP_CHANGED, self.onKickPointViable)
        self._eventmanager.register(EVENT_BALL_IN_FRAME, self.onBallInFrame)
        # Serial event example: do one, then the other, call a cb on each
        #self._actions.turn(0.2)
        #self._actions.changeLocation(20, 0, 0)
        #SerialEvent(self._eventmanager, [EVENT_TURN_DONE, EVENT_WALK_DONE], [self.onSerialExampleWalkDone, self.onSerialExampleTurnDone])
        
        self._eventmanager.register(EVENT_YGLP_POSITION_CHANGED,   lambda: pr("Yellow left seen"))
        self._eventmanager.register(EVENT_YGRP_POSITION_CHANGED, lambda: pr("Yellow right seen"))
        self._eventmanager.register(EVENT_ALL_BLUE_GOAL_SEEN,   lambda: pr("Blue goal seen"))
        self._eventmanager.register(EVENT_ALL_YELLOW_GOAL_SEEN, lambda: pr("Yellow goal seen"))

    def onSerialExampleTurnDone(self):
        print "1"

    def onSerialExampleWalkDone(self):
        print "2"
        
    def onStop(self):
        super(Template, self).onStop()

#    def onKickPointViable(self):
#        print "Kick point viable:", self._world.computed.kp

    def onBallSeen(self):
        print "Ball Seen!"
        print "Ball x: %f" % self._world.ball.centerX
        print "Ball y: %f" % self._world.ball.centerY

    def onBallInFrame(self):
        #print "ball bearing, dist %3.3f %3.3f" % (self._world.ball.bearing, self._world.ball.dist)
        pass

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Template).run()

