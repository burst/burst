#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst_events import BALL_MOVING_PENALTY
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from burst.actions.goalie.alignment_after_leap import AlignmentAfterLeap

TIME_STAY_ON_SIDE = 2 # time to wait on side when getting up
TIME_STAY_ON_BELLY = 3 # time to wait on belly when getting up
TIME_BEFORE_REGISTERING_LEAP = 5 # time to wait when head is focusing on the ball (allowing updated data to accumulate)

realLeap = True

class PenaltyGoalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self._world.ball.shouldComputeIntersection = True
        self.targetFinder = TargetFinder(actions=self._actions, targets=[self._world.ball], start=False)
        self.targetFinder.setOnTargetFoundCB(self.targetFound)
        self.targetFinder.setOnSearchFailedCB(self.searchFailed)

    def _start(self, firstTime = False):
        self.readyToLeap()

    def readyToLeap(self):
        self._actions.say("Ready to leap")
        self._actions.setCameraFrameRate(20)
        self.isLeaping = False
        self.targetFinder.start()

    def targetFound(self):
        self.targetFinder.stop()
        self._eventmanager.callLater(TIME_BEFORE_REGISTERING_LEAP, self.registerLeapPenalty)

    def registerLeapPenalty(self):
        self._eventmanager.register(self.leapPenalty, BALL_MOVING_PENALTY)

    def searchFailed(self):
        print "at searchFailed"
        # ball search failed, needs to be restarted
        if self._actions.searcher.stopped:
            self.log("Restarting target finder since searcher is stopped")
            if not self.targetFinder.stopped:
                self.log("TODO - targetFinder should have been stopped at searchFailure")
            self.targetFinder.stop()
            self._eventmanager.callLater(0.5, self.targetFinder.start)

    def leapPenalty(self, stopped=False):
        print "Penalty leap!"
        self._eventmanager.unregister(self.leapPenalty)
        if self._world.ball.dy < 0:
            if realLeap:
                self.isLeaping = True
                print "real leap right"
                self._player.unregisterFallHandling()
                self._actions.executeLeapRight().onDone(self.waitingOnRight)
            else:
                self._actions.say("right.")
                self.waitingOnRight()
        else:
            if realLeap:
                self.isLeaping = True
                print "real leap left"
                self._player.unregisterFallHandling()
                self._actions.executeLeapLeft().onDone(self.waitingOnLeft)
            else:
                self._actions.say("left.")
                self.waitingOnLeft()

    def waitingOnRight(self):
        print "wait on right"
        self._eventmanager.callLater(TIME_STAY_ON_SIDE, self.waitingOnRightGROUND)

    def waitingOnLeft(self):
        print "wait on left"
        self._eventmanager.callLater(TIME_STAY_ON_SIDE, self.waitingOnLeftGROUND)

    def waitingOnRightGROUND(self):
        print "wait on ground"
        self._eventmanager.callLater(TIME_STAY_ON_BELLY, self.gettingUpRight)

    def waitingOnLeftGROUND(self):
        print "wait on ground"
        self._eventmanager.callLater(TIME_STAY_ON_BELLY, self.gettingUpLeft)

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
            # If we're at penalty, do not align and do not leap again (to avoid scoring an own goal by mistake, or
            # touching the ball outside the penalty box)
            pass
        else:
            self.readyToLeap()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(PenaltyGoalie).run()
