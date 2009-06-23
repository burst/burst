#!/usr/bin/python

import player_init
import math
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves as moves
from burst.actions.target_finder import TargetFinder
from burst_consts import CAMERA_WHICH_TOP_CAMERA, CAMERA_WHICH_BOTTOM_CAMERA


DESIRED_DISTANCE_FROM_GOAL = 80 # In centimeters.
SAFETY_MARGIN = 30
BEARING_THRESHOLD_WHEN_APPROACHING_OWN_GOAL = 0.2 # In radians.
WIDTH_THRESHOLD_WHEN_APPROACHING_OWN_GOAL = 80


class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)
        self.debug = True

    def _start(self, firstTime=False):
#        super(Goalie, self).onStart()
        self._reset()
        # TODO: ownGoal according to my own team color.
        self.ownGoal = [self._world.ygrp, self._world.yglp]
        self.oppositeGoal = [self._world.ygrp, self._world.yglp]
        self._actions.setCameraFrameRate(10)

        # TODO: This will no longer be the case once we make sure that our own goal, regardless of the color, is at (0, 0).
        self.ownGoalGlobalCartesianCoordinates = (0.0, 0.0)

        self._restart()

    def _reset(self):
        pass

    def _report(self, string):
        if self.debug:
            self._actions.say(string)

    def _restart(self):
        self._report("In play.")
        self.onFinishedGettingUp()
#        self._report("baba.")

    def onFinishedGettingUp(self):
        if self._world.robot.sensors.isOnBack(): # TODO: Shouldn't this be in Robot?
            self._report("Back.")
            self.onFallDownOnBack()
        elif self._world.robot.sensors.isOnBelly(): # TODO: Shouldn't this be in Robot?
            self._report("Belly.")
            self.onFallDownOnBelly()
        else:
            self._report("Up.")
#            self._eventmanager.register(self.onFallDownOnBack, EVENT_ON_BACK)
#            self._eventmanager.register(self.onFallDownOnBelly, EVENT_ON_BELLY)
            self.findOutLocation()
    
    def onFallDownOnBack(self):
        self._report("onFallDownOnBack")
        self._actions.clearFootsteps()
        self._eventmanager.unregister(self.onFallDownOnBack, EVENT_ON_BACK)
        self._actions.executeGettingUpBack().onDone(self.onFinishedGettingUp)

    def onFallDownOnBelly(self):
        self._report("onFallDownOnBelly")
        self._actions.clearFootsteps()
        self._eventmanager.unregister(self.onFallDownOnBelly, EVENT_ON_BELLY)
        self._actions.executeGettingUpBack().onDone(self.onFinishedGettingUp)

    def findOutLocation(self):
        self._report("Finding location.")
        self._actions.searcher.search_one_of(targets=self.ownGoal, center_on_targets=True).onDone(lambda: self.alignTowardsOnePostOfOwnGoal(False))

    def alignTowardsOnePostOfOwnGoal(self, post_selected=True):
        self._report("alignTowardsOnePostOfOwnGoal")
        # TODO: Am I still up?
        if not post_selected:
            self.closest_goalpost = self.closestOwnGoalPost()
#            self._eventmanager.register(self.printer, EVENT_STEP)
            self._actions.tracker.track(self.closest_goalpost)
        print "Closest goal post distance, bearing:", self.closest_goalpost.dist, self.closest_goalpost.bearing
        # Regardless of the bearing, if the robot is close enough to the goal post...
        if self.closest_goalpost.width >= WIDTH_THRESHOLD_WHEN_APPROACHING_OWN_GOAL:
            self.onArrivedNextToOneGoalPostOfOwnGoal()
        # If the robot's not close enough to the goal post yet, it needs to align itself in its direction.
        elif abs(self.closest_goalpost.bearing) > BEARING_THRESHOLD_WHEN_APPROACHING_OWN_GOAL:
            self._actions.turn(self.closest_goalpost.bearing).onDone(self.alignTowardsOnePostOfOwnGoal)
        # If the robot's not close enough yet, but it's already aligned with the goal post...
        else:
            self.walkTowardsOnePostOfOwnGoal()

    def printer(self):
        print self.closest_goalpost.dist

    def walkTowardsOnePostOfOwnGoal(self):
        self._report("walkTowardsOnePostOfOwnGoal")
        if self.closest_goalpost.width >= WIDTH_THRESHOLD_WHEN_APPROACHING_OWN_GOAL:
            print "width", self.closest_goalpost.width
            self.onArrivedNextToOneGoalPostOfOwnGoal()
        else:
            distanceToWalk = self.closest_goalpost.dist - SAFETY_MARGIN
            print "Walking:", distanceToWalk
            self._actions.changeLocationRelative(distanceToWalk).onDone(self.alignTowardsOnePostOfOwnGoal)

    def onArrivedNextToOneGoalPostOfOwnGoal(self):
        self._report("onArrivedNextToOneGoalPostOfOwnGoal")
        direction = 1 if self.closest_goalpost in [self._world.yglp, self._world.bglp] else -1
        self._actions.turn(direction*math.pi/4).onDone(self.findOtherGoalPostOfOwnGoalTurnStep)

#alignAccordingToOppositeGoalSearchingStep

    def findOtherGoalPostOfOwnGoalTurnStep(self):
        self._report("findOtherGoalPostOfOwnGoalTurnStep")
        self.otherPostOfOwnGoal = self.ownGoal[1] if self.ownGoal[0] == self.closest_goalpost else self.ownGoal[0]
        self._actions.tracker.stop().onDone( # XXX 1
            lambda: self._actions.setCamera(CAMERA_WHICH_TOP_CAMERA).onDone(
            lambda: self._actions.searcher.search(targets=[self.otherPostOfOwnGoal], center_on_targets=True).onDone(
            self.onOtherPostOfOwnGoalFound)))

    def onOtherPostOfOwnGoalFound(self):
        self._report("onOtherPostOfOwnGoalFound")
        self._actions.setCamera(CAMERA_WHICH_TOP_CAMERA).onDone(
            lambda: self._actions.tracker.track(self.otherPostOfOwnGoal)) # XXX 1
        self._eventmanager.quit()

    def alignAccordingToOppositeGoalMovementStep(self, first=True):
        self._report("alignAccordingToOppositeGoalMovementStep")
        self._eventmanager.quit()
        self.relevantOppositeGoalPost = self._actions.searcher.seen_objects[0]
#        while True:
#            if self.relevantOppositeGoalPost.bearing < -ALIGNING_ACCORDING_TO_OPPOSITE_THRESHOLD:
#                self._actions.

    def closestOwnGoalPost(self):
        self._report("closestOwnGoalPost")
        if not self.ownGoal[0].seen and not self.ownGoal[1].seen:
            raise Exception("Trace me.")
        if self.ownGoal[0].seen ^ self.ownGoal[1].seen:
            for post in self.ownGoal:
                if post.seen:
                    return post
        if self.ownGoal[0].dist < self.ownGoal[1].dist:
            return self.ownGoal[0]
        else:
            return self.ownGoal[1]

    def finishedWalkingTowardsOnGoal(self):
        self._report("finishedWalkingTowardsOnGoal")
        pass

    def ownGoalRelativeCoordinates(self):
        self._report("ownGoalRelativeCoordinates")
        rightPost = self.toCartesian(self.ownGoal[0].bearing, self.ownGoal[0].dist)
        leftPost  = self.toCartesian(self.ownGoal[1].bearing, self.ownGoal[1].dist)
        x = (rightPost[0]+leftPost[0])/2
        y = (rightPost[1]+leftPost[1])/2
        print x,y
        return (x,y)

    def toCartesian(self, bearing, dist):
        self._report("toCartesian")
        return (dist*math.cos(bearing), dist*math.sin(bearing))



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
