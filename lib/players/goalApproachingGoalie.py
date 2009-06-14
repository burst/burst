#!/usr/bin/python

import player_init
import math
from burst.player import Player
from burst.events import *
from burst_consts import *
import burst.moves as moves



class Goalie(Player):

    def __init__(self, *args, **kw):
        super(Goalie, self).__init__(*args, **kw)
        self.debug = True

    def onStart(self):
#        super(Goalie, self).onStart()
        self._reset()
        self.ownGoal = [self._world.bgrp, self._world.bglp]
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
#        self._report("gaga.")
        if self._world.falldetector.isOnBack(): # TODO: Shouldn't this be in Robot?
            self._report("Back.")
            self.onFallDownOnBack()
        elif self._world.falldetector.isOnBelly(): # TODO: Shouldn't this be in Robot?
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
        self._actions.searcher.search_one_of(targets=self.ownGoal, center_on_targets=True).onDone(self.goToOwnGoal)

    def goToOwnGoal(self):
        delta_x, delta_y = self.ownGoalRelativeCoordinates()
        self._actions.changeLocationRelative(605.0-delta_x, 0.0-delta_y).onDone(self.finishedWalkingTowardsOnGoal)

    def finishedWalkingTowardsOnGoal(self):
        pass

    ###

    def ownGoalRelativeCoordinates(self):
        rightPost = toCartesian(self.ownGoal[0].bearing, self.ownGoal[0].dist)
        leftPost  = toCartesian(self.ownGoal[1].bearing, self.ownGoal[1].dist)
        x = (rightPost[0]+leftPost[0])/2
        y = (rightPost[1]+leftPost[1])/2
        return (x,y)

    def toCartesian(self, bearing, dist):
        return (dist*math.cos(bearing), dist*math.sin(bearing))



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
