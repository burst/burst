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
from burst.consts import *
import burst.moves as moves
from math import cos, sin
import time

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0
TIME_WAITING = 6 #time to finish leap and waiting

class goalie(Player):
#    def onStop(self):
#        super(Goalie, self).onStop()

    def onStart(self):
   
        self._actions.initPoseAndStiffness().onDone(self.goalieInitPos)

    def goalieInitPos(self):
        self._actions.executeMove(moves.SIT_POS).onDone(self.watchIncomingBall)   

    def watchIncomingBall(self):
        self._eventmanager.register(EVENT_BALL_BODY_INTERSECT_UPDATE, self.leap)

    def leap(self):
        self._eventmanager.unregister(EVENT_BALL_BODY_INTERSECT_UPDATE)
        print self._world.ball.body_isect
        if self._world.ball.body_isect < 0 and self._world.ball.body_isect > -(GOAL_BORDER + ERROR_IN_LENGTH):
            self._actions.say("leap right")
            self.waitingOnRight()
        elif self._world.ball.body_isect > 0 and self._world.ball.body_isect < (GOAL_BORDER + ERROR_IN_LENGTH):
            self._actions.say("leap left")
            self.watingOnLeft()   
        else:
            self.watchIncomingBall()

    def waitingOnRight(self):
        self._eventmanager.setTimeoutEventParams(TIME_WAITING, oneshot=True, cb=self.gettingUpRight)

    def watingOnLeft(self):
        self._eventmanager.setTimeoutEventParams(TIME_WAITING, oneshot=True, cb=self.gettingUpLeft)


    def gettingUpRight(self):
        #self._actions.say("up right").onDone(self.getUpBelly)
        self.getUpBelly()

    def gettingUpLeft(self):
        #self._actions.say("up left").onDone(self.getUpBelly)
        self.getUpBelly()

    def getUpBelly(self):
        #self._actions.say("up Belly").onDone(self.watchIncomingBall)
        self.watchIncomingBall()



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(goalie).run()

