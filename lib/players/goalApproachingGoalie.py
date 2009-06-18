#!/usr/bin/python

import player_init
import math
from burst.player import Player
from burst.events import *
from burst_consts import *
import burst.moves as moves

DESIRED_DISTANCE_FROM_GOAL = 50 # In centimeters.
SAFETY_MARGIN = 30
BEARING_THRESHOLD_WHEN_APPROACHING_OWN_GOAL = 0.15 # In radians.

class Goalie(Player):

    def __init__(self, *args, **kw):
        super(Goalie, self).__init__(*args, **kw)
        self.debug = True

    def onStart(self):
#        super(Goalie, self).onStart()
        self._reset()
        # TODO: ownGoal according to my own team color.
        self.ownGoal = [self._world.bgrp, self._world.bglp]
        self.oppositeGoal = [self._world.ygrp, self._world.yglp]
        self._actions.setCameraFrameRate(10)

        # TODO: This will no longer be the case once we make sure that our own goal, regardless of the color, is at (0, 0).
        self.ownGoalGlobalCartesianCoordinates = (0.0, 0.0)

        self.enterGame()

    def _reset(self):
        pass

    def _report(self, string):
        if self.debug:
            self._actions.say(string)

    def enterGame(self):
        self._report("In play.")
        self._actions.initPoseAndStiffness().onDone(self.onFinishedGettingUp)
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
        self._actions.clearFootsteps()
        self._eventmanager.unregister(self.onFallDownOnBack, EVENT_ON_BACK)
        self._actions.executeGettingUpBack().onDone(self.onFinishedGettingUp)

    def onFallDownOnBelly(self):
        self._actions.clearFootsteps()
        self._eventmanager.unregister(self.onFallDownOnBelly, EVENT_ON_BELLY)
        self._actions.executeGettingUpBack().onDone(self.onFinishedGettingUp)

    def findOutLocation(self):
        self._report("Finding location.")
        self._actions.searcher.search_one_of(targets=self.ownGoal, center_on_targets=True).onDone(lambda: self.alignTowardsOnePostOfOwnGoal(False))

    def alignTowardsOnePostOfOwnGoal(self, post_selected=True):
        # TODO: Am I still up?
        if not post_selected:
            self.closest_goalpost = self.closestOwnGoalPost()
            self._eventmanager.register(self.printer, EVENT_STEP)
            self._actions.tracker.track(self.closest_goalpost)
        if self.closest_goalpost.dist <= DESIRED_DISTANCE_FROM_GOAL:
            self.onArrivedNextToOneGoalPostOfOwnGoal()
        threshold = BEARING_THRESHOLD_WHEN_APPROACHING_OWN_GOAL
        if abs(self.closest_goalpost.bearing) < threshold:
            self.walkTowardsOnePostOfOwnGoal()
        else:
            self._actions.turn(self.closest_goalpost.bearing).onDone(self.alignTowardsOnePostOfOwnGoal)

    def printer(self):
        return
        print self.closest_goalpost.dist

    def walkTowardsOnePostOfOwnGoal(self):
        if self.closest_goalpost.dist <= DESIRED_DISTANCE_FROM_GOAL:
            self.onArrivedNextToOneGoalPostOfOwnGoal()
        else:
            distanceToWalk = self.closest_goalpost.dist - SAFETY_MARGIN
            self._actions.changeLocationRelative(distanceToWalk).onDone(self.alignTowardsOnePostOfOwnGoal)

    def onArrivedNextToOneGoalPostOfOwnGoal(self):
        print 'Got there!'
        self._eventmanager.quit()

    def closestOwnGoalPost(self):
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
        
    '''
    def goToOwnGoal(self):
        self._report("Going towards own goal.")
        relative_x, relative_y = self.ownGoalRelativeCoordinates()
        base_x, base_y = self.ownGoalGlobalCartesianCoordinates
        self._actions.changeLocationRelative(relative_x-base_x, relative_y-base_y).onDone(self.finishedWalkingTowardsOnGoal)
    '''

    def finishedWalkingTowardsOnGoal(self):
        pass

    ###

    def ownGoalRelativeCoordinates(self):
        rightPost = self.toCartesian(self.ownGoal[0].bearing, self.ownGoal[0].dist)
        leftPost  = self.toCartesian(self.ownGoal[1].bearing, self.ownGoal[1].dist)
        x = (rightPost[0]+leftPost[0])/2
        y = (rightPost[1]+leftPost[1])/2
        print x,y
        return (x,y)

    def toCartesian(self, bearing, dist):
        return (dist*math.cos(bearing), dist*math.sin(bearing))



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
