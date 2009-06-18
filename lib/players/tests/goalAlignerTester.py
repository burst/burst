#!/usr/bin/python

import player_init
from burst.player import Player
import burst.events as events
from burst.actions.headtracker import Searcher
import burst
import burst.moves as moves
from burst_consts import (LEFT, RIGHT, DEFAULT_NORMALIZED_CENTERING_Y_ERROR,
    IMAGE_CENTER_X, IMAGE_CENTER_Y, PIX_TO_RAD_X, PIX_TO_RAD_Y)

class GoalAlignerTester(Player):

    def onStart(self):
        self._actions.initPoseAndStiffness()
        self.goalposts = [self._world.yglp, self._world.ygrp]
        self.movement_deferred = None
        self.searchGoalPosts()
        
    def searchGoalPosts(self):
        self._actions.tracker.stop()
        self.goalpost_to_track = None
        self._actions.setCameraFrameRate(20)
        self._actions.search(self.goalposts, stop_on_first=True, center_on_targets=False).onDone(self.onGoalPostFound)

    def onGoalPostFound(self):
        print "Search finished"
        
        # select a sighted goal post
        for t in self.goalposts:
            if t.centered_self.sighted:
                if t.centered_self.sighted_centered:
                    print "%s sighted centered" % t.name
                    self.goalpost_to_track = t
                else:
                    print "%s sighted" % t.name
                    # update goalpost_to_track, but only if not already set (as to not override sighted_centered) 
                    if self.goalpost_to_track is None:
                        self.goalpost_to_track = t
            else:
                print "%s NOT sighted" % t.name
        
        if self.goalpost_to_track is None:
            print "ERROR! no goalpost to track!"
            self._eventmanager.quit()
        else:
            # track goal post, align against it
            self.goalLocationKnown = True
            self._actions.setCameraFrameRate(20)
            
            print "manually centering on goal post (from search goal results)"
            self.manualCentering(self.goalpost_to_track.centered_self, self.onSearchCenteringDone)

    def onSearchCenteringDone(self):
        self._actions.track(self.goalpost_to_track, self.onLostGoal)
        self.strafe()

    def onLostGoal(self):
        print "GOAL LOST, clearing footsteps, stopping strafing"
        self.goalLocationKnown = False
        if self.movement_deferred != None:
            self.movement_deferred.clear()
        self._actions.clearFootsteps().onDone(self.searchGoalPosts)
    
    def strafe(self):
        print "strafing"
        if self.goalLocationKnown:
            # TODO: Add align-to-goal-center support
            if self.goalpost_to_track.bearing < -DEFAULT_NORMALIZED_CENTERING_Y_ERROR:
                self._actions.setCameraFrameRate(10)
                if burst.connecting_to_webots():
                    self.movement_deferred = self._actions.turn(-0.2)
                    self.movement_deferred.onDone(self.strafe)
                else:
                    self.movement_deferred = self._actions.executeTurnCW()
                    self.movement_deferred.onDone(self.strafe)
            elif self.goalpost_to_track.bearing > DEFAULT_NORMALIZED_CENTERING_Y_ERROR:
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
                #self.ballLocationKnown = False
                #self._actions.setCameraFrameRate(20)
                #self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_BOTTOM).onDone(self.doNextAction)
                self._eventmanager.quit()
        else:
            print "Goalpost lost, restart search"
            self.searchGoalPosts()

    def manualCentering(self, centeredTarget, onDoneCallback):
        print "XXX Moving towards and centering on target - (%1.2f, %1.2f, %1.2f, %1.2f)" % (centeredTarget.head_yaw, centeredTarget.head_pitch, centeredTarget.centerX, centeredTarget.centerY)
        a1 = centeredTarget.head_yaw, centeredTarget.head_pitch
        a2 = (a1[0] - PIX_TO_RAD_X * (centeredTarget.centerX - IMAGE_CENTER_X),
              a1[1] + PIX_TO_RAD_Y * (centeredTarget.centerY - IMAGE_CENTER_Y))
        self._actions.moveHead(*a2).onDone(onDoneCallback)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(GoalAlignerTester).run()

