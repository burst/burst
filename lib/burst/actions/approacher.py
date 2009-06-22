from twisted.internet.defer import log

from burst.behavior import Behavior
from burst_util import succeed, polar2cart
from target_finder import TargetFinder

class Approacher(Behavior):
    """ Get close to a specified location. The location is specified by
     the given callback implicitly, so we can easily implement:
     * go to constant world position (calculate difference)
     * go to constant relative position (i.e. will do a circle of some sort)
     * go towards seen target (like BallKicker, or start of Goalie)
     * anything else (Goalie goal approach)

     Missing: any way to say how often we will call target_pos_callback, or
     on what condition. (should be another callback, errback).
    """
    def __init__(self, actions, target_pos_callback):
        super(Approacher, self).__init__(actions, 'Approacher')

        self._target_pos_callback = target_pos_callback

    def _start(self, firstTime=False):
        self._getTargetPos()

    def _getTargetPos(self):
        self._target_pos_callback().addCallback(self._approach).addErrback(log.err)

    def _approach(self, result_xy):
        if self._world.movecoordinator.isMotionInProgress():
            print "Approacher: motion still in progress, waiting on MotionBd"
            self._actions.getCurrentMotionBD().onDone(self._approach)

        x, y = result_xy

        # Verily, here be ugliness
        print "Approacher: Approaching %3.2f, %3.2f" % (x, y)

        (side, kp_x, kp_y, kp_dist, kp_bearing, target_location,
                kick_side_offset) = calcTargetXY(x, y)

        ### DECIDE ON NEXT MOVEMENT ###
        # TODO? - remove BALL language and change to TARGET language?
        # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
        if target_location == BALL_IN_KICKING_AREA:
            self.callOnDone()
            return

        # We have not reached the target yet, move towards it
        if target_location in (BALL_FRONT_NEAR, BALL_FRONT_FAR):
            self.log("Walking straight!")
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
            self.log("Side-stepping!")
            self._actions.setCameraFrameRate(10)
            self._movement_type = MOVE_SIDEWAYS
            self._movement_location = target_location
            self._movement_deferred = self._actions.changeLocationRelativeSideways(
                0.0, kp_y*MOVEMENT_PERCENTAGE_SIDEWAYS, walk=walks.SIDESTEP_WALK)
        elif target_location in (BALL_DIAGONAL, BALL_SIDE_FAR):
            self.log("Turning!")
            self._actions.setCameraFrameRate(10)
            # if we do a significant turn, our goal-alignment isn't worth much anymore...
            if kp_bearing > 10*DEG_TO_RAD:
                self._aligned_to_goal = False
            self._movement_type = MOVE_TURN
            self._movement_location = target_location
            self._movement_deferred = self._actions.turn(kp_bearing*MOVEMENT_PERCENTAGE_TURN)
        else:
            self.log("!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!")
            #import pdb; pdb.set_trace()

        print "Movement STARTING!"
        self._movement_deferred.onDone(lambda _, nextAction=self._approachBall: self._onMovementFinished(nextAction))


        self._actions.changeLocationRelative()

def getTargetPosition(x, y):
    robot = actions._world.robot
    our_x, our_y, our_heading = robot.world_x, robot.world_y, robot.world_heading
    dx, dy = x - our_x, y - our_y
    sh, ch = sin(our_heading), cos(our_heading)
    rel_x, rel_y = dx * ch - dy * ch, dx * sh + dy * ch # TODO - check me
    return succeed((rel_x, rel_y))

def ApproacheXY(actions, x, y):
    return Approacher(actions, lambda: succeed(getTargetPosition(x, y)))

def ApproachXYActiveLocalization(actions, x, y):
    return Approacher(actions, lambda: actions.localize().getDeferred().addCallback(lambda _: getTargetPosition(x, y)).addErrback(log.err))

def ApproachTarget(actions, target):
    # TODO - I think this doesn't stop right. Should really do the Behavior thing
    # to make sure stop cleans up.
    def getTargetPosition(_):
        bearing, dist = target.bearing, target.dist
        return polar2cart(dist, bearing)
    return Approacher(actions, lambda: actions.search([target]).getDeferred().addCallback(getTargetPosition).addErrback(log.err))

def ApproachTargetWithFinder(actions, target):
    # TODO - I think this doesn't stop right. Should really do the Behavior thing
    # to make sure stop cleans up.
    def getTargetPosition(_):
        bearing, dist = target.bearing, target.dist
        return polar2cart(dist, bearing)
    targetFinder = TargetFinder([target])
    approacher = Approacher(actions, lambda: actions.search([target]).getDeferred().addCallback(getTargetPosition).addErrback(log.err))
    approacher.onDone(targetFinder.stop()) # first onDone, so will be called first.
    return approacher

