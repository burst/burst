#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst.events import *
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0
TIME_WAITING = 3 #time to wait when finishing the leap for getting up
WAITING_FOR_HEAD = 5
WAITING = 6

debug = True
isWebots = False
realLeap = False

'''
0. Make sure the current goalie and goalieTester work as expected.
1. Merge goalie and goalieTester.
2. Make sure one can turn off/on the calculation of the intersection, since not all players need this functionality, and for them, it results
   in wasted CPU cycles.

'''


class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self._world.ball.shouldComputeIntersection = True

    def _start(self, firstTime=False):
#        super(Goalie, self).onStart() # Either this or the self.enterGame() at the end of this event, but not both.
        self.isPenalty = True # TODO: Use the gameStatus object.
        self._restart()
    
    def _restart(self):
        self._report("in play")
        self.whichBehavior() # Either this or the super(Goalie, self).onStart() at the start of this event, but not both.

    def _report(self, string):
        if debug:
            self._actions.say(string)

    def whichBehavior(self):
        if self.isPenalty:
            self._eventmanager.callLater(WAITING_FOR_HEAD, self.penaltyRegister)
        else:
            self.watchIncomingBall()

    def penaltyRegister(self):
        self.targetFinder = TargetFinder(actions=self._actions, targets=[self._world.ball], start=False)
        self.targetFinder.start()
        self._eventmanager.register(self.leapPenalty, BALL_MOVING_PENALTY)

    def watchIncomingBall(self):
        self.targetFinder = TargetFinder(actions=self._actions, targets=[self._world.ball], start=False)
        self.targetFinder.start()
        self._eventmanager.register(self.leap, EVENT_BALL_BODY_INTERSECT_UPDATE)
        if isWebots:
            self._eventmanager.register(self.returnHead, EVENT_BALL_LOST)

    def returnHead(self):
        self._eventmanager.unregister(self.returnHead)
        self._actions.executeHeadMove(poses.HEAD_MOVE_FRONT_FAR)
        
    def leapPenalty(self):
        self._eventmanager.unregister(self.leapPenalty)
        self.targetFinder.stop()
        print self._world.ball.dy
        if self._world.ball.dy < 0:
            if realLeap:
                self._actions.executeLeapRight().onDone(self.waitingOnRight)
            else:
                self._actions.say("Leap right.")
                self.waitingOnRight()
        else:
            if realLeap:
                self._actions.executeLeapLeft().onDone(self.waitingOnLeft)
            else:
                self._actions.say("Leap left.")
                self.waitingOnLeft()
            
    def leap(self):
        self._eventmanager.unregister(self.leap) # (EVENT_BALL_BODY_INTERSECT_UPDATE)
        self.targetFinder.stop()
        if isWebots:
            self._eventmanager.unregister(self.returnHead)
        #print self._world.ball.body_isect
        if self._world.ball.body_isect < 0 and self._world.ball.body_isect > -(GOAL_BORDER + ERROR_IN_LENGTH):
            if realLeap:
                self._actions.executeLeapRightSafe().onDone(self.waitingOnRight)
            else:
                self._actions.say("Leap right.")
                self.waitingOnRight()
        elif self._world.ball.body_isect > 0 and self._world.ball.body_isect < (GOAL_BORDER + ERROR_IN_LENGTH):
            if realLeap:
                self._actions.executeLeapLeftSafe().onDone(self.waitingOnLeft)
            else:
                self._actions.say("Leap left.")
                self.waitingOnLeft()
        else:
            self.watchIncomingBall()
            #assert(self._eventmanager.isregistered(self.returnHead))

    def waitingOnRight(self):
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpRight)

    def waitingOnLeft(self):
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpLeft)


    def gettingUpRight(self):
        if realLeap:
            self._actions.executeToBellyFromLeapRight().onDone(self.getUpBelly)
        else:
            self.onLeapComplete()

    def gettingUpLeft(self):
        if realLeap:
            self._actions.executeToBellyFromLeapLeft().onDone(self.getUpBelly)
        else:
            self.onLeapComplete()

    def getUpBelly(self):
        self._actions.executeGettingUpBelly().onDone(self.onLeapComplete)
        
    def onLeapComplete(self):
        if realLeap:
            self._report("Leap complete.")
            self._eventmanager.quit()
        else:
            self._restart()


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
