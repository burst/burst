from math import sin, cos

from twisted.internet.defer import log

from burst.behavior import Behavior

from burst.behavior_params import (calcTargetXY,
    # Area types (where is the ball, err, target, in relation to me)
    BALL_IN_KICKING_AREA, BALL_FRONT_NEAR, BALL_FRONT_FAR, BALL_BETWEEN_LEGS, BALL_SIDE_NEAR,
    BALL_DIAGONAL, BALL_SIDE_NEAR, BALL_SIDE_FAR,
    # Other stuff
    MOVEMENT_PERCENTAGE_TURN,
    # Movement types (for logging)
    MOVE_FORWARD, MOVE_SIDEWAYS, MOVE_TURN
    )

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
        """ This can potentially take a long time (localize) or be instantaneous. Since
        we just need an x,y coming out of this and into _approach, we don't care. Also,
        you are free to have a side running TargetFinder and just give us the best result
        here. If you return None, we stop. """
        self._target_pos_callback().addCallback(self._approach).addErrback(log.err)

    def _approach(self, result_xy):
        """
        do a single movement towards the target location given by target_pos_callback
        """

        if self._actions.isMotionInProgress():
            self.log("motion still in progress, waiting for original onDone")
            return

        if result_xy is None:
            self.log("WARNING: short circuited by returning None from target_pos_callback")
            self.stop()
            self.callOnDone()
            return

        x, y = result_xy

        # Verily, here be ugliness
        self.log("_approach %3.2f, %3.2f" % (x, y))

        (side, kp_x, kp_y, kp_dist, kp_bearing, target_location,
                kick_side_offset) = calcTargetXY(x, y)

        ### DECIDE ON NEXT MOVEMENT ###
        # TODO? - remove BALL language and change to TARGET language?
        # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
        if target_location == BALL_IN_KICKING_AREA:
            self.stop()
            self.callOnDone()
            return

        def move_forward(target_location):
            return (self._actions.changeLocationRelative(kp_x*MOVEMENT_PERCENTAGE_FORWARD), MOVE_FORWARD)
            # TODO - the obstacle thing
            if self._obstacle_in_front and target_location == BALL_FRONT_FAR:
                opposite_side_from_obstacle = self.getObstacleOppositeSide()
                print "opposite_side_from_obstacle: %d" % opposite_side_from_obstacle
                return (self._actions.changeLocationRelativeSideways(
                    0.0, 30.0*opposite_side_from_obstacle, walk=walks.SIDESTEP_WALK), MOVE_SIDEWAYS)
            else:
                return (self._actions.changeLocationRelative(kp_x*MOVEMENT_PERCENTAGE_FORWARD), MOVE_FORWARD)

        def move_sideways(target_location):
            return (self._actions.changeLocationRelativeSideways(
                0.0, kp_y*MOVEMENT_PERCENTAGE_SIDEWAYS, walk=walks.SIDESTEP_WALK), MOVE_SIDEWAYS)

        def move_turn(target_location):
            return self._actions.turn(kp_bearing*MOVEMENT_PERCENTAGE_TURN), MOVE_TURN

        type_to_msg = {MOVE_FORWARD:'Walking straight',
            MOVE_SIDEWAYS:'Side-stepping!', MOVE_TURN:'Turning!'}

        action_selection = dict(sum(
            [[(area, movement) for area in areas] for areas, movement in
                (((BALL_FRONT_NEAR, BALL_FRONT_FAR), move_forward),
                 ((BALL_BETWEEN_LEGS, BALL_SIDE_NEAR), move_sideways),
                 ((BALL_DIAGONAL, BALL_SIDE_FAR), move_turn))]
            , []))

        bd = None
        if area in action_selection:
            self._actions.setCameraFrameRate(10)
            bd, movement_type = action_selection[area](target_location)
        self.log(type_to_msg.get(movement_type, "!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! ball location problematic!"))
        bd.onDone(self._getTargetPos)

def getTargetPosition(actions, x, y):
    import pdb; pdb.set_trace()
    robot = actions._world.robot
    our_x, our_y, our_heading = robot.world_x, robot.world_y, robot.world_heading
    dx, dy = x - our_x, y - our_y
    sh, ch = sin(-our_heading), cos(-our_heading)
    rel_x, rel_y = dx * ch - dy * ch, dx * sh + dy * ch # TODO - check me
    print "getTargetPosition: rel_x = %3.2f cm, rel_y = %3.2f cm (dx %3.2f, dy %3.2f, head %3.2f)" % (
        rel_x, rel_y, dx, dy, our_heading)
    return succeed((rel_x, rel_y))

def ApproacheXY(actions, x, y):
    return Approacher(actions, lambda: succeed(getTargetPosition(actions, x, y)))

def ApproachXYActiveLocalization(actions, x, y):
    return Approacher(actions, lambda: actions.localize().getDeferred().addCallback(
        lambda _: getTargetPosition(actions, x, y)).addErrback(log.err))

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

