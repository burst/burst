#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst_events import EVENT_BALL_BODY_INTERSECT_UPDATE
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from burst.actions.goalie.alignment_after_leap import AlignmentAfterLeap

HALF_GOAL_WIDTH = 65
ERROR_IN_LENGTH = 20
WAITING_FOR_NEW_DATA = 1  #not to use old data (made when head was searching)
SEARCH_TIME = 0.3 #threshHold for the searcher to work before ruin history data.
SLOW_BALL_TIME = 3 #not leaping for slow balls
FAST_BALL_TIME = 0.1 #not leaping for too fast ball, since the robot won't make it

realLeap = True

class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self._world.ball.shouldComputeIntersection = True
        self.targetFinder = TargetFinder(actions=self._actions, targets=[self._world.ball], start=False)
        self.targetFinder.setOnTargetFoundCB(self.targetFound)
        self.targetFinder.setOnTargetLostCB(self.targetLost)
        self.targetFinder.setOnSearchFailedCB(self.searchFailed)

    def _start(self, firstTime = False):
        self.targetLostTime = self._world.time
        self.targetFoundTime = self.targetLostTime + SEARCH_TIME + 0.1
        self._eventmanager.register(self.leap, EVENT_BALL_BODY_INTERSECT_UPDATE)    
        self.readyToLeap()

    def readyToLeap(self):
        self._actions.say("Ready to leap")
        self._actions.setCameraFrameRate(20)
        self.isLeaping = False
        self.targetFinder.start()

    def targetFound(self):
        self.targetFoundTime = self._world.time

    def targetLost(self):
        self.targetLostTime = self._world.time

    def searchFailed(self):
        print "at searchFailed"
        # ball search failed, needs to be restarted
        if self._actions.searcher.stopped:
            self.log("Restarting target finder since searcher is stopped")
            if not self.targetFinder.stopped:
                self.log("TODO - targetFinder should have been stopped at searchFailure")
            self.targetFinder.stop()
            self._eventmanager.callLater(0.5, self.targetFinder.start)

    leap_time = -1
    def leap(self, stopped=False):
        if self.isLeaping: return
        
        if self.targetFoundTime - self.targetLostTime > SEARCH_TIME:
            if self.targetFoundTime + WAITING_FOR_NEW_DATA > self._world.time: #waiting WAITING_FOR_NEW_DATA: meaning not entering the method
                print "LEAP ABORTED, NOT ENOUGH DATA!"
                return

        print "Checking if leap is necessary"
        if self._world.time == self.leap_time:
            print "LEAP TWICE IN SAME TURN!!!! BUG!!!!"
            return
        self.leap_time = self._world.time
        if self._world.ball.isTimeCalc and not \
         (FAST_BALL_TIME < self._world.ball.time_intersection < SLOW_BALL_TIME):
            print "According to time calculation, decided not to leap"
            print "Time of arrival: ", self._world.ball.time_intersection
            return  
        if (-(HALF_GOAL_WIDTH + ERROR_IN_LENGTH) < self._world.ball.body_isect < 0):
            print "LEAPING RIGHT************###############"
            self.isLeaping = True
            self.targetFinder.stop()
            if realLeap:
                print "real leap right safe"
                self._player.unregisterFallHandling()
                self._actions.executeLeapRight().onDone(self.gettingUpRight)
            else:
                self._actions.say("right.")
                self.gettingUpRight()
        elif 0 < self._world.ball.body_isect < (HALF_GOAL_WIDTH + ERROR_IN_LENGTH):
            print "LEAPING LEFT@@@@@@@@@@@@@@@@@@@@@@@@@@"
            self.isLeaping = True
            self.targetFinder.stop()
            if realLeap:
                print "real leap left safe"
                self._player.unregisterFallHandling()
                self._actions.executeLeapLeft().onDone(self.gettingUpLeft)
            else:
                self._actions.say("left.")
                self.gettingUpLeft()
        else:
            print "Decided not to leap right now..."

    def gettingUpRight(self):
        print "getting up right"
        if realLeap:
            self._actions.executeToBellyFromLeapRight().onDone(lambda _=None: self.getUpBelly())
        else:
            self.onGettingUpDone()

    def gettingUpLeft(self):
        print "getting up left"
        if realLeap:
            self._actions.executeToBellyFromLeapLeft().onDone(lambda _=None: self.getUpBelly())
        else:
            self.onGettingUpDone()

    def getUpBelly(self):
        self._actions.executeGettingUpBelly().onDone(lambda _=None: self.onGettingUpDone())

    def onGettingUpDone(self):
        print "Getting up done"
        self._player.registerFallHandling()
        if realLeap:
#            AlignmentAfterLeap(self._actions, side).start().onDone(lambda _=None: self._actions.executeMove(poses.SIT_POS).onDone(self.readyToLeap))
            #AlignmentAfterLeap(self._actions, side).start().onDone(self.readyToLeap)
            if not self._player._main_behavior.stopped:
                print "stopping existing behavior before turning into Kicker"
                self._player._main_behavior.stop() # TODO - use returned bd
            self._player.turnToKicker()
        else:
            self.readyToLeap()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
