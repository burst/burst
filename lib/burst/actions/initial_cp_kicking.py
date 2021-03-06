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

#===============================================================================
#    Logic for Kicking behavior:
#
# 1. Scan for ball
# 2. Advance towards ball (while tracking ball)
# 3. When near ball, circle-strafe (to correct direction) till goal is seen and centered (goal is tracked)
# 4. Search ball down, align against ball and kick
#
# Handling Sonar data (obstacles):
# When obstacle encountered DURING move:
# * stop move only if it's a long walk (if it's a short walk to the ball, we prefer not to stop...)
# When obstacle encountered BEFORE move:
# * Kicking: change kick to inside-kick/angle-kick if obstacle is at center
#   (Goalie->inside kick towards opposite side, Kicker-> angle-kick towards field center)
# * Ball far: side-step to opposite side (or towards field center if at center)
#
# TODO's:
# * RESET self._aligned_to_goal when needed
#===============================================================================

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
        self._clearMovement(clearFootsteps = True)

        stop_bd = succeedBurstDeferred(self)
        if self._currentFinder:
            print "STOPPING CURRENT FINDER: %s" % self._currentFinder.name
            stop_bd = self._currentFinder.stop()
        return stop_bd

    ################################################################################
    # Handling movements
    #
    def _clearMovement(self, clearFootsteps = False):
        if self._movement_deferred:
            self._movement_deferred.clear()
            if clearFootsteps and self._movement_type in (MOVE_FORWARD, MOVE_SIDEWAYS, MOVE_TURN, MOVE_ARC):
                print "CLEARING FOOTSTEPS!"
                self._actions.clearFootsteps()
        self._movement_deferred = None
        self._movement_type = None
        self._movement_location = None

    def _onMovementFinished(self, nextAction):
        print "Movement DONE!"
        self._clearMovement(clearFootsteps = False)
        nextAction()

    def _stopOngoingMovement(self, forceStop = False):
        # stop movement if we're forced or if it's a long walk-forward move
        shouldStopMovement = forceStop or (self._movement_type == MOVE_FORWARD and self._movement_location == BALL_FRONT_FAR)
        if shouldStopMovement:
            self._clearMovement(clearFootsteps = True)

        print "Kicking: _stopOngoingMovement: current movement %s (forceStop = %s)" % (shouldStopMovement and "STOPPED" or "CONTINUES", forceStop)

    ################################################################################
    # Sonar callbacks
    #
    def onObstacleSeen(self):
        self._obstacle_in_front = self._sonar.getLastReading()
        print "Obstacle seen (on %s, distance of %f)!" % (self._obstacle_in_front)

        if self._movement_deferred:
            # if walking forward and ball is far, stop
            if self._movement_type == MOVE_FORWARD and self._movement_location == BALL_FRONT_FAR:
                print "NOTE: Obstacle seen while a movement is in progress, movement STOPPED"
                self._stopOngoingMovement(forceStop = True)
                self._eventmanager.callLater(0.5, self._approachBall)
            else:
                print "NOTE: Obstacle seen while a movement is in progress, movement CONTINUES"

    def onObstacleLost(self):
        print "Obstacle lost!"
        self._obstacle_in_front = None

    def onObstacleInFrame(self):
        #print "Obstacle in frame!"
        self._obstacle_in_front = self._sonar.getLastReading()
        #print "Obstacle seen (on %s, distance of %f)!" % (self._obstacle_in_front)

    def getObstacleOppositeSide(self):
        if self._obstacle_in_front == None:
            print "NO OBSTACLE DATA?"
            opposite_side_from_obstacle = 0
        elif self._obstacle_in_front[0] == "center":
            opposite_side_from_obstacle = random.choice((-1,1))
        elif self._obstacle_in_front[0] == "left":
            opposite_side_from_obstacle = -1
        elif self._obstacle_in_front[0] == "right":
            opposite_side_from_obstacle = 1
        return opposite_side_from_obstacle

    ################################################################################
    # _approachBall helpers (XXX - should they be submethods of _approachBall? would
    # make it cleared to understand the relationship, not require this comment)
    #
    def _approachBall(self):
        print ("\nApproaching %s: (recently seen %s, dist: %3.3f, distSmoothed: %3.3f, bearing: %3.3f)"+"\n"+"-"*100) % (
                  self._target.name, self._target.recently_seen, self._target.dist, self._target.distSmoothed, self._target.bearing)

        # TODO: we probably need a better solution? this can happen after we're aligned,
        # when ball tracker finds the ball while a previous movement is still ON.
        if self._movement_deferred:
            print "LAST MOVEMENT STILL ON!!!"
            #import pdb; pdb.set_trace()
            return

        if not self._target.recently_seen:
            if self._ballFinder.stopped:
                print "TARGET LOST, RESTARTING BALL FINDER"
                self.switchToFinder(to_goal_finder=False)
            else:
                print "TARGET LOST, RELYING ON SEARCHER"
            # TODO: searcher / searcher CB should take care of finding target, behavior should take care of turning when search fails
            return

        (side, kp_x, kp_y, kp_dist, kp_bearing, target_location, kick_side_offset) = calcTarget(self._target.distSmoothed, self._target.bearing)
        side = self._side
        ### DECIDE ON NEXT MOVEMENT ###
        
        # Ball inside kicking area, kick it
        if target_location == BALL_BETWEEN_LEGS and (self._aligned_to_goal or not self._align_to_target):
            # TODO: diagonalize the kick. It might be off target even if we think we are alligned            
            self.doKick(side)
            return

        if target_location in (BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS) and not self._aligned_to_goal and self._align_to_target and not self._diag_kick_tested:
            print "NEW CODE: Searching goal post!"
            self._diag_kick_tested = True
            (ball_x, ball_y) = polar2cart(self._target.distSmoothed, self._target.bearing)
            self._ballY_lastseen = ball_y
            self._side_last = side
            if self._ballFinder:

                self._ballFinder.stop().onDone(lambda: self.doKick(self._side))

            return

        self._diag_kick_tested = False
        
        # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
        # TODO: Use 2x circle strafing to get to the ball faster an not so accurate
        #if target_location in (BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT_NEAR) and not self._aligned_to_goal and self._align_to_target:
        #    self.logverbose("Aligning to goal! (switching to goal finder)")
        #    self._actions.setCameraFrameRate(20)
        #    self.switchToFinder(to_goal_finder=True)
        #    return
        
        if target_location in (BALL_FRONT_NEAR, BALL_FRONT_FAR):
            self.logverbose("Walking straight!")
            self._actions.setCameraFrameRate(10)
            self._movement_type = MOVE_FORWARD
            self._movement_location = target_location
            if self._obstacle_in_front and target_location == BALL_FRONT_FAR:
                opposite_side_from_obstacle = self.getObstacleOppositeSide()
                print "opposite_side_from_obstacle: %d" % opposite_side_from_obstacle
                # if we do a significant side-stepping, our goal-alignment isn't worth much anymore...
                self._aligned_to_goal = False
                self._movement_type = MOVE_SIDEWAYS
                self._movement_deferred = self._actions.changeLocationRelativeSideways(
                    0.0, 30.0*opposite_side_from_obstacle, walk=walks.SIDESTEP_WALK)

#                        self._movement_type = MOVE_CIRCLE_STRAFE
#                        if opposite_side_from_obstacle == -1:
#                            strafeMove = self._actions.executeCircleStrafeCounterClockwise
#                        else:
#                            strafeMove = self._actions.executeCircleStrafeClockwise
#                        self._movement_deferred = self._actions.executeCircleStraferInitPose().onDone(strafeMove)

            else:
                self._movement_deferred = self._actions.changeLocationRelative(min(kp_x*MOVEMENT_PERCENTAGE_FORWARD,MAX_FORWARD_WALK))
        elif target_location in (BALL_IN_KICKING_AREA, BALL_SIDE_NEAR):
            self.logverbose("Side-stepping!")
            self._actions.setCameraFrameRate(10)
            movementAmount = min(kp_y*MOVEMENT_PERCENTAGE_SIDEWAYS,MAX_SIDESTEP_WALK)
            # if we do a significant side-stepping, our goal-alignment isn't worth much anymore...
            if movementAmount > 20:
                self._aligned_to_goal = False
            self._movement_type = MOVE_SIDEWAYS
            self._movement_location = target_location
            # TODO: change numbers for side stepping. Does that 4 or 5 times.                            
            self._movement_deferred = self._actions.changeLocationRelativeSideways(
                0.0, movementAmount, walk=walks.SIDESTEP_WALK)
        elif target_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
            self.logverbose("Turning!")
            self._aligned_to_goal = False
            self._actions.setCameraFrameRate(10)
            movementAmount = kp_bearing*MOVEMENT_PERCENTAGE_TURN
            # if we do a significant turn, our goal-alignment isn't worth much anymore...
            if movementAmount > 10*DEG_TO_RAD:
                self._aligned_to_goal = False
            self._movement_type = MOVE_TURN
            self._movement_location = target_location
            self._movement_deferred = self._actions.turn(movementAmount)
        else:
            self.logverbose("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")
            #import pdb; pdb.set_trace()

        print "Movement STARTING!"
        self._movement_deferred.onDone(lambda _, nextAction=self._approachBall: self._onMovementFinished(nextAction))

    def doKick(self, side):
        # Look for goal, decide if can skip adjustments and kick ball diagonally
        self.logverbose("Kicking!")
        if self._currentFinder:
            self._currentFinder.stop()
            self._currentFinder = None
        #        self.logverbose("kick_side_offset: %3.3f" % (kick_side_offset))
        self._actions.setCameraFrameRate(10)
        self._movement_type = MOVE_KICK
        self._movement_location = BALL_BETWEEN_LEGS

        #if self._obstacle_in_front and self._obstacle_in_front[0] == "center":
            # TODO: Change to angle-kick towards left/right side of goal (except for Goalie)
        self._movement_deferred = self._actions.inside_kick(burst.actions.KICK_TYPE_INSIDE, side)
        #else:
        #    self._movement_deferred = self._actions.adjusted_straight_kick(side, kick_side_offset)
        self._movement_deferred.onDone(self.stop)

    def switchToFinder(self, to_goal_finder=False):
        from_finder = self._ballFinder
        to_finder = self._ballFinder
    #    if to_goal_finder:
    #        from_finder, to_finder = self._ballFinder, self._ballFinder
    #    else:
            # switch to bottom camera when we look for the ball
            # --- DONT DO THIS UNTIL IMOPS CODE DOES THE SWITCHING, or segfault for you ---
            #self._actions.setCamera(burst_consts.CAMERA_WHICH_BOTTOM_CAMERA)
        pass
        stop_bd = from_finder.stop()
        print "SwitchToFinder: calling %s.start" % (to_finder.name)
        self._currentFinder = to_finder
        # TODO: Yet More Hacks
        doit = lambda f: self._eventmanager.callLater(0.0, f) if not stop_bd.completed() else stop_bd.onDone(f)
        doit(to_finder.start)


    ################################################################################
    # Checking goal position before kicking

    #    def searchGoalPost(self):
    #        self._currentFinder = None
    #        self._actions.searcher.search_one_of(self.target_left_right_posts, center_on_targets=False).onDone(self.onSearchGoalPostOver)

    #def onSearchGoalPostOver(self):
    #    self._actions.say('onSearchGoalPostOver')
    #    
    #    # calculate target bearing (position inside goal)
    #    nearestGoalpost = None
    #    if self.target_left_right_posts[0].centered_self.sighted:
    #        nearestGoalpost = self.target_left_right_posts[0]
    #    if self.target_left_right_posts[1].centered_self.sighted:
    #        if not nearestGoalpost or abs(nearestGoalpost.bearing) > self.target_left_right_posts[1].bearing:
    #            nearestGoalpost = self.target_left_right_posts[1]
    #            
    #    if nearestGoalpost is None:
    #        self._eventmanager.callLater(0.0, self._approachBall)
    #        return
    #    
    #    # Add offset to the diagonal kick (so we'll align not on the actual goalpost, but on about 1/4 of the goal)
    #    targetBearing = nearestGoalpost.bearing
    #    if nearestGoalpost == self._world.opposing_lp:
    #        targetBearing = targetBearing + 0.5/2
    #    elif nearestGoalpost == self._world.opposing_rp:
    #        targetBearing = targetBearing - 0.5/2 # TODO: Move to const, calibrate value (cover half-goal? goal? differs for different distances?)
    #    
    #    # check if diagonal kick is viable
    #    # use self._ballY_lastseen
    #    kick_side_offset = getKickingType(self, targetBearing, self._ballY_lastseen, self._side_last, margin=0)
    #    if kick_side_offset is None:
    #        self._eventmanager.callLater(0.0, self._approachBall)
    #    else:
    #        # do diagonal kick
    #        self.doKick(self._side_last)

    ################################################################################
    # Strafing

    #def onGoalFound(self):
    #    
    #    self.logverbose('onGoalFound')
    #    if not self._is_strafing:
    #        self.goalpost_to_track = self._goalFinder.getTargets()[0]

    #        # Add offset to the goalpost align (so we'll align not on the actual goalpost, but on about 1/4 of the goal)
    #        if self.goalpost_to_track == self._world.opposing_lp:
    #            self.alignLeftLimit = -0.5
    #            self.alignRightLimit = 0
    #        elif self.goalpost_to_track == self._world.opposing_rp:
    #            self.alignLeftLimit = 0
    #            self.alignRightLimit = 0.5 # TODO: Move to const, calibrate value (cover half-goal? goal? differs for different distances?)

    #        g = self.goalpost_to_track
    #        self.logverbose('onGoalFound: found %s at %s, %s (%s)' % (g.name, g.centerX, g.centerY, g.seen))
    #        self.strafe()

    #def strafe(self):
    #    self._is_strafing = True

    #    if not self.goalpost_to_track.seen:
    #        self.logverbose("strafe: goal post not seen")
    #        # Eran: Needed? won't goal-post searcher wake us up? Can't this create a case where strafe is called twice?
    #        self._eventmanager.callLater(self._eventmanager.dt, self.strafe)
    #        return
    #    self.logverbose("strafe: goal post seen")
    #    self.logverbose("%s bearing is %s. Left is %s, Right is %s" % (self.goalpost_to_track.name, self.goalpost_to_track.bearing, self.alignLeftLimit, self.alignRightLimit))
    #    # TODO: Add align-to-goal-center support
    #    if self.goalpost_to_track.bearing < self.alignLeftLimit:
    #        strafeMove = self._actions.executeCircleStrafeClockwise
    #    elif self.goalpost_to_track.bearing > self.alignRightLimit:
    #        strafeMove = self._actions.executeCircleStrafeCounterClockwise
    #    else:
    #        self._is_strafing = False
    #        self._is_strafing_init_done = False
    #        self.logverbose("Aligned position reached! (starting ball search)")
    #        self._aligned_to_goal = True
    #        self._actions.setCameraFrameRate(20)
    #        if self._goalFinder:
    #            self._goalFinder.stop().onDone(self.refindBall)
    #        else:
    #            self.refindBall()
    #        return

    #    # TODO: FPS=10 removed for now (for accurate feedback), might be needed for stable circle-strafing!
    #    #self._actions.setCameraFrameRate(10)

    #    self._movement_type = MOVE_CIRCLE_STRAFE
    #    self._movement_location = BALL_BETWEEN_LEGS
    #    if not self._is_strafing_init_done:
    #        self.logverbose("Aligning and strafing...")
    #        self._is_strafing_init_done = True
    #        self._movement_deferred = self._actions.executeCircleStraferInitPose().onDone(strafeMove)
    #    else:
    #        self.logverbose("Strafing...")
    #        self._movement_deferred = strafeMove()

    #    # We use call later to allow the strafing to handle the correct image (otherwise we get too much strafing)
    #    nextAction = lambda _: self._onMovementFinished(lambda: self._eventmanager.callLater(0.2, self.strafe))

    #    print "Movement STARTING! (strafing)"
    #    self._movement_deferred.onDone(nextAction)

    def refindBall(self):
        self._currentFinder = None
        self._actions.executeHeadMove(poses.HEAD_MOVE_FRONT_BOTTOM).onDone(
            # TODO: Fix distSmooth after moving head - this is just a workaround
            lambda: self._eventmanager.callLater(0.5,
                 lambda: self.switchToFinder(to_goal_finder=False)))

