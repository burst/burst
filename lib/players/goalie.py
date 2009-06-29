#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from burst.actions.goalie.alignment_after_leap import left, right, AlignmentAfterLeap

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0
TIME_WAITING = 3 #time to wait when finishing the leap for getting up
WAITING_FOR_HEAD = 5
WAITING = 6
WAITING_FOR_NEW_DATA = 1  #not to use old data (made when head was searching)

debug = True
realLeap = True
debugLeapRight = False
debugLeapLeft = False



class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self._world.ball.shouldComputeIntersection = True
        self.targetFinder = TargetFinder(actions=self._actions, targets=[self._world.ball], start=False)

    def _start(self, firstTime=False):
        #AlignmentAfterLeap(self._actions, right).start()
        #return
        self.isPenalty = False # TODO: Use the gameStatus object.
        self.targetFinder.setOnTargetFoundCB(self.targetFound)
        self.targetFinder.setOnTargetLostCB(self.targetLost)
        self.targetLostTime = self._world.time

    def _start(self, firstTime=False):
        self.readyToLeap()

    def readyToLeap(self):
        print "readyToLeap"
        self.targetFinder.start()

    def targetFound(self):
        self.targetFoundTime = self._world.time
        if self.isPenalty:
            self.targetFinder.stop()
            self._eventmanager.register(self.leapPenalty, BALL_MOVING_PENALTY)
        else:
            before = len(self._eventmanager._registered)
            self._eventmanager.register(self.leap, EVENT_BALL_BODY_INTERSECT_UPDATE)
            after = len(self._eventmanager._registered)
            print "registering: self: %s %s, #registered: before %s, after %s" % (
                id(self), id(self.leap), before, after) # note: id(self.leap) changes, but it's ok.

    def targetLost(self):
        self.targetLostTime = self._world.time
        if self.isPenalty:
            self._eventmanager.unregister(self.leapPenalty)
        else:
            self._eventmanager.unregister(self.leap)

    def leapPenalty(self, stopped=False):
        if self.targetFoundTime + WAITING_FOR_HEAD < self._world.time:
            print "LEAP (PENALTY) ABORTED, NOT ENOUGH DATA!"
            return
        print "Penalty leap!"
        self._eventmanager.unregister(self.leapPenalty)
        #print self._world.ball.dy
        if self._world.ball.dy < 0:
            if realLeap or debugLeapRight:
                print "real leap right"
                self._actions.executeLeapRight().onDone(self.waitingOnRight)
            else:
                self._actions.say("Leap right.")
                self.waitingOnRight()
        else:
            if realLeap or debugLeapLeft:
                print "real leap left"
                self._actions.executeLeapLeft().onDone(self.waitingOnLeft)
            else:
                self._actions.say("Leap left.")
                self.waitingOnLeft()
                
    leap_time = -1
    def leap(self, stopped=False):
        if self.targetFoundTime - self.targetLostTime > 0.5:
            if self.targetFoundTime + WAITING_FOR_NEW_DATA < self._world.time:
                print "LEAP ABORTED, NOT ENOUGH DATA!"
                return

        print "Checking if leap is necessary"
        if self._world.time == self.leap_time:
            import pdb; pdb.set_trace()
        self.leap_time = self._world.time
        if self._world.ball.body_isect < 0 and self._world.ball.body_isect > -(GOAL_BORDER + ERROR_IN_LENGTH) or debugLeapRight:
            print "Leaping right!"
            self._eventmanager.unregister(self.leap) # (EVENT_BALL_BODY_INTERSECT_UPDATE)
            self.targetFinder.stop()
            if realLeap:
                print "real leap right safe"
                self._actions.executeLeapRightSafe().onDone(self.waitingOnRight)
            else:
                self._actions.say("Leap right.")
                self.waitingOnRight()
        elif self._world.ball.body_isect > 0 and self._world.ball.body_isect < (GOAL_BORDER + ERROR_IN_LENGTH) or debugLeapLeft:
            print "Leaping left!"
            self._eventmanager.unregister(self.leap) # (EVENT_BALL_BODY_INTERSECT_UPDATE)
            self.targetFinder.stop()
            if realLeap:
                print "real leap left safe"
                self._actions.executeLeapLeftSafe().onDone(self.waitingOnLeft)
            else:
                self._actions.say("Leap left.")
                self.waitingOnLeft()
        else:
            print "Decided not to leap right now..."

    def waitingOnRight(self):
        print "wait on right"
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpRight)

    def waitingOnLeft(self):
        print "wait on left"
        self._eventmanager.callLater(TIME_WAITING, self.gettingUpLeft)

    def gettingUpRight(self):
        print "getting up right"
        if realLeap:
            self._actions.executeToBellyFromLeapRight().onDone(lambda: self.getUpBelly(right))
        else:
            self.onLeapComplete(right)

    def gettingUpLeft(self):
        print "getting up left"
        if realLeap:
            self._actions.executeToBellyFromLeapLeft().onDone(lambda: self.getUpBelly(left))
        else:
            self.onLeapComplete(left)

    def getUpBelly(self, side):
        self._actions.executeGettingUpBelly().onDone(lambda: self.onLeapComplete(side))

    def onLeapComplete(self, side):
        print "complete"    
        if realLeap:
            AlignmentAfterLeap(self._actions, side).start().onDone(lambda: self._actions.executeMove(poses.SIT_POS).onDone(self.readyToLeap))
        else:
            self.readyToLeap()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()

