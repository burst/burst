#!/usr/bin/python

import player_init
import burst_field
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from burst.actions.goalie.alignment_after_leap import left, right, AlignmentAfterLeap
from math import pi, sqrt, acos
from burst_consts import FOV_X, IMAGE_WIDTH
DESIRED_DISTANCE_FROM_GOAL_LINE = 17 * 0.055

debug = True

# TODO: Centering bugs?
# TODO: Realign the head after first centering? Probably shouldn't.
# TODO: 

class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)
        self.side = left

    def _start(self, firstTime=False):
        # TODO - remove
        def donothing(*args, **kw):
            pass
        self._eventmanager._mainloop._player.onFallen = donothing
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
        for goalpost in filter(lambda obj: obj.seen, [self._world.our_rp, self._world.our_lp, self._world.our_goal.unknown]):
            if (goalpost.centerX > burst_consts.IMAGE_CENTER_X if self.side == left else goalpost.centerX < burst_consts.IMAGE_CENTER_X):
                self.cb.clear() # TODO: Is this OK even if the cb has already been called? Is being called?
                self._eventmanager.unregister(self.monitorForFirstOwnGoalPost, EVENT_STEP)
                self.onGoalPostFoundAndReadyForCentering(goalpost)

    def onGoalPostFoundAndReadyForCentering(self, goalpost):
        print "onGoalPostFoundAndReadyForCentering"from burst_consts import
        self._actions.clearFootsteps().onDone(lambda _: self._centerOnGoal(goalpost))
        
            #lambda _=None, _goalpost1=goalpost: self._actions.centerer.start(target=_goalpost1).onDone(
            #lambda _=None, _goalpost2=goalpost: self.onCenteredOnFirstGoalpost(_goalpost2)))

    def centerOnGoal(self, goalpost):
        #Pretty simple: when the goalpost is in the left part of the frame - move head and body left, else move right when in the middle - done
        #Get current bearing - will give aproximate angle 
        goalpost.centerX 
    def onCenteredOnFirstGoalpost(self, goalpost):
        print "onCenteredOnFirstGoalpost"
        self.distanceToFirst = goalpost.dist
        goalpost.centered_self.clear()
        print "!", self.distanceToFirst
        self._actions.moveHead(self.side*pi/2, -40.0*DEG_TO_RAD).onDone(self.onReadyToLookForSecond)

    def onReadyToLookForSecond(self):
        self._eventmanager.register(self.monitorForSecondOwnGoalPost, EVENT_STEP)
        self._actions.turn(self.side*2*pi)

    def monitorForSecondOwnGoalPost(self):
        # Get the closest currently seen goal post of our own goal:
        for obj in filter(lambda _obj: _obj.seen, 
                [self._world.our_rp, self._world.our_lp, self._world.our_goal.unknown]):
            readyForCentering = (
                # 0.45-0.55 is a deadzone, since the first goalpost might appear to move back slightly.
                0.10*burst_consts.IMAGE_WIDTH_INT < obj.centerX < 0.35*burst_consts.IMAGE_WIDTH_INT
                if self.side == left
                else 0.90*burst_consts.IMAGE_WIDTH_INT > obj.centerX > 0.65*burst_consts.IMAGE_WIDTH_INT)
            # If that goal post is past the middle of what we see, stop and focus on it:
            if readyForCentering:
                self._eventmanager.unregister(self.monitorForSecondOwnGoalPost, EVENT_STEP)                
                self._actions.clearFootsteps().onDone(
                    lambda _=None, _obj1=obj: self._actions.centerer.start(target=_obj1).onDone(
                    lambda _=None, _obj2=obj: self.onCenteredOnSecondGoalpost(_obj2)))
                break

    def onCenteredOnSecondGoalpost(self, obj):
        print "onCenteredOnSecondGoalpost"
        for x in [self._world.our_rp, self._world.our_lp, self._world.our_goal.unknown]:
            print x, "seen: %s dist: %3.3f bearing: %3.3f" % (x.seen, x.dist, x.bearing)
            print "centered dist:", x.centered_self.dist
        print "chosen:", obj.centered_self.dist, obj
        self.distanceToSecond = obj.dist
        print "first, second:", self.distanceToFirst, self.distanceToSecond
        self.analyze()

    def analyze(self):
        print "analyze"
        a, b, c = burst_field.CROSSBAR_CM_WIDTH, self.distanceToFirst, self.distanceToSecond
#        a, b, c = 140.0, 211.0, 290.0 # TODO: REMOVE THIS LINE!
        print a, b, c
        m = sqrt( (2*b*b + 2*c*c - a*a) / 4.0 )
        alpha = acos( (b*b+c*c-a*a)/(2.0*b*c) )
        print "analyzed distance:", m, "analyzed degree:", alpha
        self._actions.changeHeadAnglesRelative(-0.5*alpha, 0.0).onDone(
            lambda _=None, alpha=alpha, m=m: self.onHeadDirectedAtCenterOfGoal(alpha, m))
        
    def onHeadDirectedAtCenterOfGoal(self, alpha, m):
        print "onHeadDirectedAtCenterOfGoal"
        rad = self._world.getAngle('HeadYaw')
        self._actions.moveHead(0.0, -40.0*DEG_TO_RAD).onDone(
            lambda: self._actions.turn(rad).onDone(
            lambda: self._actions.changeLocationRelative(m).onDone(
            self.onArrivalAtMiddleOfOwnGoal)))

    def onArrivalAtMiddleOfOwnGoal(self):
        print "onArrivalAtMiddleOfOwnGoal"
        self._eventmanager.register(self.monitorForOppositeGoal, EVENT_STEP)
        self._actions.turn(2*pi)

    def monitorForOppositeGoal(self):
#        print "monitorForOppositeGoal"
        opp = filter(lambda obj: obj.seen, [self._world.opposing_rp, self._world.opposing_lp,
            self._world.opposing_goal.unknown])
        for goalpost in opp:
            if 0.25*IMAGE_WIDTH < goalpost.centerX < 0.75*IMAGE_WIDTH:
                self._eventmanager.unregister(self.monitorForOppositeGoal, EVENT_STEP)
                self._actions.clearFootsteps().onDone(self.onAlignedWithOppositeGoal)

    def onAlignedWithOppositeGoal(self):
        print "onAlignedWithOppositeGoal"
        self._eventmanager.register(self.shittyCode, EVENT_STEP)

    def shittyCode(self):
        print "shittyCode"
        self._eventmanager.unregister(self.shittyCode, EVENT_STEP)
        self._actions.changeLocationRelative(DESIRED_DISTANCE_FROM_GOAL_LINE).onDone(self.onFinished)

    def onFinished(self):
        print "onFinished"
        self._eventmanager.quit()



if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
