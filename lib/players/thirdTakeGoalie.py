#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from burst.actions.goalie.alignment_after_leap import left, right, AlignmentAfterLeap
from math import pi


debug = True

class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)
        self.side = left

    def _start(self, firstTime=False):
        self._restart()

    def _restart(self):
        self._report("in play")
        self.positionHead()

    def _report(self, string):
        if debug:
            self._actions.say(string)

    def positionHead(self):
        print "positionHead"
        self._actions.moveHead(-self.side*pi/2, -40.0*DEG_TO_RAD).onDone(self.onHeadPositioned)

    def onHeadPositioned(self):
        print "onHeadPositioned"
        self._eventmanager.register(self.monitorForFirstOwnGoalPost, EVENT_STEP) # TODO: We could see it beforehand.
        self.cb = self._actions.moveHead(self.side*pi/2, -40.0*DEG_TO_RAD)
        self.cb.onDone(self.onHeadSweeped)

    def onHeadSweeped(self):
        print "onHeadSweeped"
        self._actions.turn(self.side*2*pi)

    def monitorForFirstOwnGoalPost(self):
#        print "monitorForFirstOwnGoalPost"
        for goalpost in filter(lambda obj: obj.seen, [self._world.our_rp, self._world.our_lp, self._world.our_goal.unknown]):
            if (goalpost.centerX > burst_consts.IMAGE_CENTER_X if self.side == left else goalpost.centerX < burst_consts.IMAGE_CENTER_X):
                self.cb.clear() # TODO: Is this OK even if the cb has already been called? Is being called?
                self._eventmanager.unregister(self.monitorForFirstOwnGoalPost, EVENT_STEP)
                self.onGoalPostFoundAndReadyForCentering(goalpost)

    def onGoalPostFoundAndReadyForCentering(self, goalpost):
        print "onGoalPostFoundAndReadyForCentering"
        self._actions.clearFootsteps().onDone(
            lambda _=None, goalpost=goalpost: self._actions.centerer.start(target=goalpost).onDone(
            lambda _=None, goalpost=goalpost: self.onCenteredOnFirstGoalpost(goalpost)))

    def onCenteredOnFirstGoalpost(self, goalpost):
        print "onCenteredOnFirstGoalpost"
        self.distanceToFirst = goalpost.centered_self.dist
        self._eventmanager.register(self.monitorForSecondOwnGoalPost, EVENT_STEP)
        self._actions.turn(self.side*2*pi)

    def monitorForSecondOwnGoalPost(self):
#        print "monitorForSecondOwnGoalPost"
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
                    lambda _=None, obj=obj: self._actions.centerer.start(target=obj).onDone(
                    lambda _=None, obj=obj: self.onCenteredOnSecondGoalpost(obj)))
                break

    def onCenteredOnSecondGoalpost(self, obj):
        print "onCenteredOnSecondGoalpost"
        self.distanceToSecond = obj.centered_self.dist
        print self.distanceToFirst, self.distanceToSecond
        self._eventmanager.quit()
        





if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()

