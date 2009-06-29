#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from burst.actions.goalie.alignment_after_leap import left, right, AlignmentAfterLeap

HALF_GOAL_WIDTH = 57
ERROR_IN_LENGTH = 5
TIME_STAY_ON_BELLY = 3 #time to wait when finishing the leap for getting up
WAITING_FOR_HEAD = 5
WAITING_FOR_NEW_DATA = 1  #not to use old data (made when head was searching)
SEARCH_TIME = 0.3 #threshHold for the searcher to work before ruin history data.
SLOW_BALL_TIME = 3 #not leaping for slow balls
FAST_BALL_TIME = 0.5 #not leaping for too fast ball, since the robot won't make it
LONG_TIME_ERROR = 0
SHORT_TIME_ERROR = 0

realLeap = False
debugLeapRight = False
debugLeapLeft = False

class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self._world.ball.shouldComputeIntersection = True
        self.targetFinder = TargetFinder(actions=self._actions, targets=[self._world.ball], start=False)
        self.targetFinder.setOnTargetFoundCB(self.targetFound)
        self.targetFinder.setOnTargetLostCB(self.targetLost)
        self.isPenalty = False # TODO: Use the gameStatus object.

    def _start(self, firstTime = False):
        #AlignmentAfterLeap(self._actions, right).start()
        #return
        self.targetLostTime = self._world.time
        self.targetFoundTime = self.targetLostTime + SEARCH_TIME + 0.1
        if not self.isPenalty:
            self._eventmanager.register(self.leap, EVENT_BALL_BODY_INTERSECT_UPDATE)    
        self.readyToLeap()
       
    def readyToLeap(self):
        print "readyToLeap"
        self._actions.setCameraFrameRate(20)
        self.isLeaping = False
        self.targetFinder.start()

    def targetFound(self):
        self.targetFoundTime = self._world.time
        if self.isPenalty:#TODO: check penalty goalie!!!
            self.targetFinder.stop()
            self._eventmanager.register(self.leapPenalty, BALL_MOVING_PENALTY)
        #else:
            #before = len(self._eventmanager._registered)
            #after = len(self._eventmanager._registered)
            #print "registering: self: %s %s, #registered: before %s, after %s" % (
            #    id(self), id(self.leap), before, after) # note: id(self.leap) changes, but it's ok.

    def targetLost(self):
        self.targetLostTime = self._world.time
        #if self.isPenalty:
            #self._eventmanager.unregister(self.leapPenalty)
        #else:
            #self._eventmanager.unregister(self.leap)

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
                self._player.unregisterFallHandling()
                self._actions.executeLeapRight().onDone(self.waitingOnRight)
            else:
                self._actions.say("right.")
                self.waitingOnRight()
        else:
            if realLeap or debugLeapLeft:
                print "real leap left"
                self._player.unregisterFallHandling()
                self._actions.executeLeapLeft().onDone(self.waitingOnLeft)
            else:
                self._actions.say("left.")
                self.waitingOnLeft()
                
    leap_time = -1
    def leap(self, stopped=False):
        if self.isLeaping: return
        
        if self.targetFoundTime - self.targetLostTime > SEARCH_TIME:
            if self.targetFoundTime + WAITING_FOR_NEW_DATA > self._world.time: #waiting WAITING_FOR_NEW_DATA: meaning not entering the method
                print "LEAP ABORTED, NOT ENOUGH DATA!"
                return

        print "Checking if leap is necessary"
        if self._world.time == self.leap_time:
            #import pdb; pdb.set_trace()
            print "LEAP TWICE IN SAME TURN!!!! BUG!!!!"
            return
        self.leap_time = self._world.time
        if self._world.ball.isTimeCalc and not \
         (FAST_BALL_TIME + SHORT_TIME_ERROR < self._world.ball.time_intersection < SLOW_BALL_TIME + LONG_TIME_ERROR):
            print "According to time calculation, decided not to leap"
            print "Time of arrival: ", self._world.ball.time_intersection
            return  
        if (-(HALF_GOAL_WIDTH + ERROR_IN_LENGTH) < self._world.ball.body_isect < 0) or debugLeapRight:
            print "Leaping right!"
            self.isLeaping = True
            self.targetFinder.stop()
            if realLeap:
                print "real leap right safe"
                self._player.unregisterFallHandling()
                self._actions.executeLeapRightSafe().onDone(self.waitingOnRight)
            else:
                self._actions.say("right.")
                self.waitingOnRight()
        elif 0 < self._world.ball.body_isect < (HALF_GOAL_WIDTH + ERROR_IN_LENGTH) or debugLeapLeft:
            print "Leaping left!"
            self.isLeaping = True
            self.targetFinder.stop()
            if realLeap:
                print "real leap left safe"
                self._player.unregisterFallHandling()
                self._actions.executeLeapLeftSafe().onDone(self.waitingOnLeft)
            else:
                self._actions.say("left.")
                self.waitingOnLeft()
        else:
            print "Decided not to leap right now..."

    def waitingOnRight(self):
        print "wait on right"
        self._eventmanager.callLater(TIME_STAY_ON_BELLY, self.gettingUpRight)

    def waitingOnLeft(self):
        print "wait on left"
        self._eventmanager.callLater(TIME_STAY_ON_BELLY, self.gettingUpLeft)

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
        self._player.registerFallHandling()        
        if realLeap:
            AlignmentAfterLeap(self._actions, side).start().onDone(lambda: self._actions.executeMove(poses.SIT_POS).onDone(self.readyToLeap))
        else:
            self.readyToLeap()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()

