'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import (BurstDeferred, succeedBurstDeferred,
    Nameable, calculate_middle, calculate_relative_pos,
    polar2cart, cart2polar, nicefloats)

# local imports
import burst
from burst_events import (EVENT_OBSTACLE_SEEN, EVENT_OBSTACLE_LOST, EVENT_OBSTACLE_IN_FRAME)
import burst.actions
from burst.actions.target_finder import TargetFinder
import burst.moves as moves
import burst.moves.walks as walks
import burst.moves.poses as poses
from burst.behavior import Behavior
from burst_consts import LEFT, RIGHT

from burst.behavior_params import (calcTarget, getKickingType, MAX_FORWARD_WALK, MAX_SIDESTEP_WALK, BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS,
                                   BALL_FRONT_NEAR, BALL_FRONT_FAR, BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL,
                                   MOVEMENT_PERCENTAGE_FORWARD, MOVEMENT_PERCENTAGE_SIDEWAYS, MOVEMENT_PERCENTAGE_TURN,
                                   MOVE_FORWARD, MOVE_ARC, MOVE_TURN, MOVE_SIDEWAYS, MOVE_CIRCLE_STRAFE, MOVE_KICK)
from burst_consts import (LEFT, RIGHT, IMAGE_CENTER_X, IMAGE_CENTER_Y,
    PIX_TO_RAD_X, PIX_TO_RAD_Y, DEG_TO_RAD)
import burst_consts
import random


class InitialKicker(Behavior):

    def __init__(self, actions, align_to_target=True, side=LEFT):
        super(InitialKicker, self).__init__(actions = actions, name = 'InitialKicker')

        self.verbose = True
	self._side = side
        self._align_to_target = align_to_target

        self._sonar = self._world.robot.sonar
        self._eventmanager.register(self.onObstacleSeen, EVENT_OBSTACLE_SEEN)
        self._eventmanager.register(self.onObstacleLost, EVENT_OBSTACLE_LOST)
        self._eventmanager.register(self.onObstacleInFrame, EVENT_OBSTACLE_IN_FRAME)

        self._ballFinder = TargetFinder(actions=actions, targets=[self._world.ball], start=False)
        self._ballFinder.setOnTargetFoundCB(self._approachBall)
        self._ballFinder.setOnTargetLostCB(self._stopOngoingMovement)
        
        #self.target_left_right_posts = target_left_right_posts
        #self._goalFinder = TargetFinder(actions=actions, targets=self.target_left_right_posts, start=False)
        #self._goalFinder.setOnTargetFoundCB(self.onGoalFound)
        
        self._currentFinder = None

    def _start(self, firstTime=False):
        self._aligned_to_goal = False
        self._diag_kick_tested = False
        self._movement_deferred = None
        self._movement_type = None
        self._movement_location = None

        self._is_strafing = False
        self._is_strafing_init_done = False

        self._obstacle_in_front = None
        self._target = self._world.ball

        self._actions.setCameraFrameRate(20)
        # kicker initial position
        self._actions.executeMove(poses.STRAIGHT_WALK_INITIAL_POSE).onDone(
            lambda: self.switchToFinder(to_goal_finder=False))

    def _stop(self):
        print "KICKING STOPS!!!"
        stop_bd = succeedBurstDeferred(self)
        return stop_bd


