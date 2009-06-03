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
import burst.moves as moves
from math import cos, sin
import time

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0
TIME_WAITING = 6 #time to wait when finishing the leap for getting up

class goalie(Player):
#    def onStop(self):
#        super(Goalie, self).onStop()
    

    def onStart(self):
        self.isPenalty = True
        
        self._actions.initPoseAndStiffness().onDone(self.goalieInitPos)

    def goalieInitPos(self):
        self._actions.executeMove(moves.SIT_POS).onDone(self.whichBehavior)
        
    def whichBehavior (self):
        if self.isPenalty:
            self._eventmanager.register(self.leapPenalty, BALL_MOVING_PENALTY)
            self.isTrackingBall = True
            self._eventmanager.register(self.trackBall, EVENT_BALL_IN_FRAME)
        else:
            self.watchIncomingBall()
        self._actions.say("ready")

    def watchIncomingBall(self):            
        self._eventmanager.register(self.leap, EVENT_BALL_BODY_INTERSECT_UPDATE)
        self.isTrackingBall = True
        self._eventmanager.register(self.trackBall, EVENT_BALL_IN_FRAME)
        
    def leapPenalty(self):
        self._eventmanager.unregister(self.leapPenalty)
        self.isTrackingBall = False
        self._eventmanager.unregister(self.trackBall)
        print self._world.ball.dy
        if self._world.ball.dy < 0:
            self._actions.say("leap right")
        else:
            self._actions.say("leap Left")
        self._eventmanager.callLater(TIME_WAITING, self.whichBehavior)
            

    def leap(self):
        self._eventmanager.unregister(self.leap)
        self.isTrackingBall = False
        self._eventmanager.unregister(self.trackBall)
        print self._world.ball.body_isect
        if self._world.ball.body_isect < 0 and self._world.ball.body_isect > -(GOAL_BORDER + ERROR_IN_LENGTH):
            self._actions.executeLeapRightSafe().onDone(self.waitingOnRight)
        elif self._world.ball.body_isect > 0 and self._world.ball.body_isect < (GOAL_BORDER + ERROR_IN_LENGTH):
            self._actions.executeLeapLeftSafe().onDone(self.watingOnLeft)   
        else:
            self.watchIncomingBall()

    def waitingOnRight(self):
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpRight)

    def watingOnLeft(self):
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpLeft)


    def gettingUpRight(self):
        self._actions.executeToBellyFromLeapRight().onDone(self.getUpBelly)

    def gettingUpLeft(self):
        self._actions.executeToBellyFromLeapLeft().onDone(self.getUpBelly)

    def getUpBelly(self):
        self._actions.executeGettingUpBelly().onDone(self.watchIncomingBall)
        
    def trackBall(self):
        if self.isTrackingBall:
            self._actions.executeTracking(self._world.ball)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(goalie).run()
