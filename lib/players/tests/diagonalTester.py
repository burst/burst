#!/usr/bin/python

import player_init
from math import fabs
from burst.behavior import InitialBehavior
from burst_events import EVENT_BALL_IN_FRAME
import burst.moves.poses as poses
from burst_util import polar2cart
from burst.actions.target_finder import TargetFinder
from burst.actions.diagonalkicker import *
import burst.behavior_params as params

class DiagonalTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.STRAIGHT_WALK_INITIAL_POSE)
        self._ballFinder = TargetFinder(actions=actions, targets=[self._world.ball], start=False)
        self._ballFinder.setOnTargetFoundCB(self.ball_found)
        self._ballFinder.setOnTargetLostCB(self.ball_lost)
        
    def _start(self, firstTime=False):
        self._actions.executeHeadMove(poses.HEAD_MOVE_FRONT_FAR).onDone(self.find_goal)
    
    def find_goal(self):
        self._actions.localize().onDone(self.found_goal)

    def found_goal(self):
        if fabs(self._world.opposing_lp.bearing - self._world.opposing_rp.bearing)<0.05:
            print "ERROR: Goal posts are the same one..., left post is: ", self._world.opposing_lp.bearing, " right post is: ", self._world.opposing_rp.bearing
            lambda: self._eventmanager.callLater(0.5, self._start)
        else:            
            opposing_lp, opposing_rp = self._world.opposing_lp, self._world.opposing_rp
            t = self._world.time
            dtl, dtr = t - opposing_lp.update_time, t - opposing_rp.update_time
            print "Goal Posts Bearings: %3.2f, %3.2f (seens %s, %s), (updated %3.2f seconds ago)" % (
                    opposing_lp.bearing, opposing_rp.bearing, opposing_lp.seen, opposing_rp.seen, max(dtl, dtr))
            
            self._actions.executeHeadMove(poses.HEAD_MOVE_FRONT_BOTTOM).onDone(
                lambda: self._eventmanager.callLater(0.5, self._ballFinder.start))
            #self._eventmanager.register(self.printBall, EVENT_BALL_IN_FRAME)
            print "So, goal center is ", (opposing_lp.bearing + opposing_rp.bearing)/2

    def ball_found(self):
        print "BALL FOUND"
        opposing_lp, opposing_rp = self._world.opposing_lp, self._world.opposing_rp
        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
        goal = (opposing_lp.bearing + opposing_rp.bearing)/2        
        (side, kick_parameter) = getKickingType(goal, ball_y, 0)
        if side == None or kick_parameter == None or not isInEllipse(ball_x, ball_y, side, 0):
            print "ERROR: could not find the right kicking parameter, side: ", side, ", parameter: ", kick_parameter, " x: ", ball_x
            (side, kick_parameter) = getKickingType(goal, ball_y, 1)
            if side == None or kick_parameter == None or not isInEllipse(ball_x, ball_y, side, 1):
                print "ERROR: STILL could not find the right kicking parameter, side: ", side, ", parameter: ", kick_parameter, " x: ", ball_x
            else:
                self._ballFinder.stop().onDone(lambda: self._actions.adjusted_straight_kick(side , kick_parameter))
        else:
            print "KICKING"            
            self._ballFinder.stop().onDone(lambda: self._actions.adjusted_straight_kick(side , kick_parameter))
        
    def ball_lost(self):
        print "BALL LOST"

    def printBall(self):

        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)
# minimal printing for spreadshit
#        print "%s, %3.3f, %3.3f, %3.3f, %3.3f, %3.3f" % (self._world.ball.seen, self._world.ball.dist,              self._world.ball.distSmoothed, self._world.ball.bearing, ball_x, ball_y)
# legible printing
        (ball_x, ball_y) = polar2cart(self._world.ball.distSmoothed, self._world.ball.bearing)        
        print "dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f, Ball x: %3.3f, Ball y: %3.3f" % 	(self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing, ball_x, ball_y)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(DiagonalTester).run()

