#!/usr/bin/python

import player_init
from burst.player import Player
import burst.events as events
from burst.actions.headtracker import Searcher
import burst
import burst.moves as moves
from burst_consts import LEFT, RIGHT, DEFAULT_CENTERING_Y_ERROR, IMAGE_CENTER_X, IMAGE_CENTER_Y, PIX_TO_RAD_X, PIX_TO_RAD_Y

class GoalAlignerTester(Player):

    def onStart(self):
        self._actions.initPoseAndStiffness()
        self.targets=[self._world.yglp, self._world.ygrp]
        
        self._actions.setCameraFrameRate(20)
        self._actions.search(self.targets, stop_on_first=True, center_on_targets=True).onDone(self.onFound)

    def onFound(self):
        print "Search finished"
        
        self.goalpost_to_track = None
        for t in self.targets:
            if t.centered_self.sighted:
                if t.centered_self.sighted_centered:
                    print "%s sighted centered" % t._name
                    self.goalpost_to_track = t
                else:
                    print "%s sighted" % t._name
                    # update goalpost_to_track, but only if not already set (as to not override sighted_centered) 
                    if not self.goalpost_to_track is None:
                        self.goalpost_to_track = t
            else:
                print "%s NOT sighted" % t._name
        
        if self.goalpost_to_track is None:
            print "ERROR! no goalpost to track!"
            self._eventmanager.quit()
        else:
            # track goal post, align against it
            self.goalLocationKnown = True
            self._actions.setCameraFrameRate(20)
            self._actions.tracker.track(self.goalpost_to_track, self.onLostGoal)
            self.strafe()

    def onLostGoal(self):
        print "GOAL LOST, clearing footsteps, stopping strafing"
        self.goalLocationKnown = False
        if self.movement_deferred != None:
            self._actions.clearFootsteps().onDone(self.movement_deferred.callOnDone)
        else:
            self.strafe()
    
    def strafe(self):
        print "strafing"
        if self.goalLocationKnown:
            # TODO: Add align-to-goal-center support
            if self.goalpost_to_track.bearing < -DEFAULT_CENTERING_Y_ERROR:
                self._actions.setCameraFrameRate(10)
                if burst.connecting_to_webots():
                    self.movement_deferred = self._actions.turn(-0.2)
                    self.movement_deferred.onDone(self.strafe)
                else:
                    self.movement_deferred = self._actions.executeTurnCW()
                    self.movement_deferred.onDone(self.strafe)
            elif self.goalpost_to_track.bearing > DEFAULT_CENTERING_Y_ERROR:
                self._actions.setCameraFrameRate(10)
                if burst.connecting_to_webots():
                    self.movement_deferred = self._actions.turn(0.2)
                    self.movement_deferred.onDone(self.strafe)
                else:
                    self.movement_deferred = self._actions.executeTurnCCW()
                    self.movement_deferred.onDone(self.strafe)
            else:
                print "Aligned position reached!"
                self._actions.tracker.stop()
                #self.aligned_to_goal = True
                #self.ballLocationKnown = False
                #self._actions.setCameraFrameRate(20)
                #self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_BOTTOM).onDone(self.doNextAction)
                self._eventmanager.quit()
        else:
            print "Goalpost lost, restart search"
            self._actions.tracker.stop()
            self._actions.setCameraFrameRate(20)
            self._actions.search([self._world.yglp, self._world.ygrp], stop_on_first=True).onDone(self.onSearchResults)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(GoalAlignerTester).run()

