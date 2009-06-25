#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from burst.actions.goalie.alignment_after_leap import left, right, AlignmentAfterLeap
from math import pi

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0
TIME_WAITING = 3 #time to wait when finishing the leap for getting up
WAITING_FOR_HEAD = 5
WAITING = 6

debug = True
isWebots = False
realLeap = True
debugLeapRight = False
debugLeapLeft = False



class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self.side = left

    def _start(self, firstTime=False):
        self.isPenalty = False # TODO: Use the gameStatus object.
        self._restart()

    def _restart(self):
        self._report("in play")
        self.positionHead()

    def _report(self, string):
        if debug:
            self._actions.say(string)

    def positionHead(self):
        self._actions.moveHead(self.side*pi/2, -40.0*DEG_TO_RAD).onDone(self.onHeadPositioned)

    def onHeadPositioned(self):
        self._eventmanager.register(self.monitorForFirstOwnGoalPost, EVENT_STEP)
        self._actions.turn(self.side*2*pi)

    def monitorForFirstOwnGoalPost(self):
        # Get the closest currently seen goal post of our own goal:
        goalpost = self._world.our_goal.unknown
        for obj in filter(lambda obj: obj.seen, [self._world.our_rp, self._world.our_lp]):
            if not goalpost.seen or obj.height * obj.width >= goalpost.height * goalpost.width:
                goapost = obj
        # If that goal post is past the middle of what we see, stop and focus on it:
        readyForCentering = (
            goalpost.centerX > burst_consts.IMAGE_CENTER_X
            if self.side == left
            else goalpost.centerX < burst_consts.IMAGE_CENTER_X)
        if readyForCentering:
            self._eventmanager.unregister(self.monitorForFirstOwnGoalPost, EVENT_STEP)
            self.onGoalPostFoundAndReadyForCentering(goalpost)

    def onGoalPostFoundAndReadyForCentering(self, goalpost):
        self._actions.clearFootsteps().onDone(
        lambda _, goalpost=goalpost: self._actions.centerer.start(target=goalpost).onDone(
        lambda _, goalpost=goalpost: self.onCenteredOnFirstGoalpost(goalpost)))

    def onCenteredOnFirstGoalpost(self, goalpost):
        self.distanceToFirst = self.goalpost.centered_self.dist
        self._eventmanager.register(self.monitorForSecondOwnGoalPost, EVENT_STEP)
        self._actions.turn(self.side*2*pi)

    def monitorForSecondOwnGoalPost(self):
        # Get the closest currently seen goal post of our own goal:
        for obj in filter(lambda obj: obj.seen, [self._world.our_rp, self._world.our_lp, self._world.our_goal.unknown]):
            readyForCentering = (
                # 0.45-0.55 is a deadzone, since the first goalpost might appear to move back slightly.
                0.25*burst_consts.IMAGE_WIDTH_INT < obj.centerX < 0.45*burst_consts.IMAGE_WIDTH_INT
                if self.side == left
                else 0.75*burst_consts.IMAGE_WIDTH_INT > obj.centerX > 0.55*burst_consts.IMAGE_WIDTH_INT)
            # If that goal post is past the middle of what we see, stop and focus on it:
            if readyForCentering:
                self._eventmanager.unregister(self.monitorForSecondOwnGoalPost, EVENT_STEP)                
                self._actions.clearFootsteps().onDone(
                    lambda _, obj=obj: self._actions.centerer.start(target=obj).onDone(
                    lambda _, obj=obj: self.onCenteredOnSecondGoalpost(obj)))
                break

    def onCenteredOnSecondGoalpost(self, obj):
        self.distanceToSecond = obj.centered_self.dist
        print "eh-hey"
        self._eventmanager.quit()
        





if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()

