from burst.behavior import Behavior

class Approacher(Behavior):
    """ get close to a specific location. Should be used for any approach, but BallKicker is
    actually a whole Approach+Align+Kick thing, that /does it differently/.
    """
    def __init__(self, actions, target_pos_callback):
        super(Approacher, self).__init__(actions, 'Approacher')
    
        self._target_pos_callback = target_pos_callback

    def _start(self, firstTime=False):
        self._bd = bd = self._make(self)
        self._actions.localize().onDone(self._approach)
        return bd

    def _approach(self):
        if self._world.movecoordinator.isMotionInProgress():
            print "Approacher: motion still in progress, waiting on MotionBd"
            self._actions.getCurrentMotionBD().onDone(self._approach)

        x, y = self._target_pos_callback()
        
        # Verily, here be ugliness
        print "Approacher: Approaching %3.2f, %3.2f" % (x, y)

        (side, kp_x, kp_y, kp_dist, kp_bearing, target_location, kick_side_offset) = calcTargetXY(x, y)

        ### DECIDE ON NEXT MOVEMENT ###
        # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
        if target_location == BALL_IN_KICKING_AREA:
            self.callOnDone()
            return

        # We have not reached the target yet, move towards it
        if target_location in (BALL_FRONT_NEAR, BALL_FRONT_FAR):
            self.debugPrint("Walking straight!")
            self._actions.setCameraFrameRate(10)
            self._movement_type = MOVE_FORWARD
            self._movement_location = target_location
            if self._obstacle_in_front and target_location == BALL_FRONT_FAR:
                opposite_side_from_obstacle = self.getObstacleOppositeSide()
                print "opposite_side_from_obstacle: %d" % opposite_side_from_obstacle

                self._movement_type = MOVE_SIDEWAYS
                self._movement_deferred = self._actions.changeLocationRelativeSideways(
                    0.0, 30.0*opposite_side_from_obstacle, walk=walks.SIDESTEP_WALK)

            else:
                self._movement_deferred = self._actions.changeLocationRelative(kp_x*MOVEMENT_PERCENTAGE_FORWARD)
        elif target_location in (BALL_BETWEEN_LEGS, BALL_SIDE_NEAR):
            self.debugPrint("Side-stepping!")
            self._actions.setCameraFrameRate(10)
            self._movement_type = MOVE_SIDEWAYS
            self._movement_location = target_location
            self._movement_deferred = self._actions.changeLocationRelativeSideways(
                0.0, kp_y*MOVEMENT_PERCENTAGE_SIDEWAYS, walk=walks.SIDESTEP_WALK)
        elif target_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
            self.debugPrint("Turning!")
            self._actions.setCameraFrameRate(10)
            # if we do a significant turn, our goal-alignment isn't worth much anymore...
            if kp_bearing > 10*DEG_TO_RAD:
                self._aligned_to_goal = False
            self._movement_type = MOVE_TURN
            self._movement_location = target_location
            self._movement_deferred = self._actions.turn(kp_bearing*MOVEMENT_PERCENTAGE_TURN)
        else:
            self.debugPrint("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")
            #import pdb; pdb.set_trace()

        print "Movement STARTING!"
        self._movement_deferred.onDone(lambda _, nextAction=self._approachBall: self._onMovementFinished(nextAction))


        self._actions.changeLocationRelative()

