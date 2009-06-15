#!/usr/bin/python

import player_init
from burst.player import Player
from burst.events import *
from burst_consts import *
import burst.moves as moves

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0
TIME_WAITING = 3 #time to wait when finishing the leap for getting up
WAITING_FOR_HEAD = 5
WAITING = 6

class GoalieTester(Player):

    def onStart(self):
        super(GoalieTester, self).onStart()
        self.isPenalty = False # TODO: Use the gameStatus object.
        self.isWebots = False
        #self.enterGame() # temporary disabling game-controller stuff

    def enterGame(self):
        self._actions.say("in play")
        self._actions.setCameraFrameRate(20)
        self._actions.initPoseAndStiffness(moves.SIT_POS).onDone(self.goalieInitPos)

    def goalieInitPos(self):
        self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_FAR).onDone(self.whichBehavior)

    def getToPosition(self):
        pass

    def whichBehavior(self):
        if self.isPenalty:
            self.isTrackingBall = True
            self._eventmanager.register(self.trackBall, EVENT_BALL_IN_FRAME)
            self._eventmanager.callLater(WAITING_FOR_HEAD, self.penaltyRegister)
        else:
            self.watchIncomingBall()

    def penaltyRegister(self):
        self._eventmanager.register(self.leapPenalty, BALL_MOVING_PENALTY)

    def watchIncomingBall(self):            
        self._eventmanager.register(self.leap, EVENT_BALL_BODY_INTERSECT_UPDATE)
        self.isTrackingBall = True
        self._eventmanager.register(self.trackBall, EVENT_BALL_IN_FRAME)
        if self.isWebots:
            self._eventmanager.register(self.returnHead, EVENT_BALL_LOST)

    def returnHead(self):
        self._eventmanager.unregister(self.returnHead)
        self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_FAR)
        
    def leapPenalty(self):
        self._eventmanager.unregister(self.leapPenalty)
        self.isTrackingBall = False
        self._eventmanager.unregister(self.trackBall)
        print self._world.ball.dy
        if self._world.ball.dy < 0:
            self._actions.say("Leap Right")
        else:
            self._actions.say("Leap Left")
        self._eventmanager.callLater(WAITING, self.whichBehavior)

    def leap(self):
        self._eventmanager.unregister(self.leap)
        self.isTrackingBall = False
        self._eventmanager.unregister(self.trackBall)
        if self.isWebots:
            self._eventmanager.unregister(self.returnHead)
        #print self._world.ball.body_isect
        if self._world.ball.body_isect < 0 and self._world.ball.body_isect > -(GOAL_BORDER + ERROR_IN_LENGTH):
            self._actions.say("Leap Right")
        elif self._world.ball.body_isect > 0 and self._world.ball.body_isect < (GOAL_BORDER + ERROR_IN_LENGTH):
            self._actions.say("Leap Left")   
        self._eventmanager.callLater(WAITING, self.watchIncomingBall)
            #assert(self._eventmanager.isregistered(self.returnHead))

    def waitingOnRight(self):
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpRight)

    def waitingOnLeft(self):
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpLeft)


    #def gettingUpRight(self):
     #   self._actions.executeToBellyFromLeapRight().onDone(self.getUpBelly)

    #def gettingUpLeft(self):
     #   self._actions.executeToBellyFromLeapLeft().onDone(self.getUpBelly)

    #def getUpBelly(self):
     #   self._actions.executeGettingUpBelly().onDone(self.onLeapComplete)
        
    def trackBall(self):
        if self.isTrackingBall:
            self._actions.executeTracking(self._world.ball)
            
   # def onLeapComplete(self):
    #    print "Leap complete"
     #   self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(GoalieTester).run()