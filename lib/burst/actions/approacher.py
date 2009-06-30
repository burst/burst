from math import sin, cos, sqrt

from twisted.internet.defer import log

from burst.behavior import Behavior

import burst.moves.walks as walks

from burst_util import succeed, polar2cart
from target_finder import TargetFinder

################################################################################

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
    def __init__(self, actions, target_pos_callback, movement_callback=None):
        """
        Arguments:
         actions - reference to Actions
         target_pos_callback - a callable returning a Deferred, whose result is
          the relative target location as a tuple (x,y,heading) which means:
          forward x, left y, turn heading (not neccessarily executed like this, but end result
          the same). (So heading of 0 for no change, negative for right turn, positive for left turn).
         movement_callback - a callable returning a BurstDeferred, no which we wait for action
          complete.
        """
        super(Approacher, self).__init__(actions, 'Approacher')
        assert(callable(target_pos_callback))
        self._target_pos_callback = target_pos_callback
        self._movement_callback = (movement_callback if movement_callback is not None
            else self._actions.changeLocationRelative)

    def _start(self, firstTime=False):
        self._getTargetPos()

    def _stop(self):
        # we assume user uses everything, so we stop everything. Override to have different behavior.
        self._actions.searcher.stop()
        self._actions.tracker.stop()
        self._actions.centerer.stop()
        self._actions.clearFootsteps()
        self._actions.localizer.stop()
        return self._actions.succeed(self)
    
    def _getTargetPos(self):
        """ This can potentially take a long time (localize) or be instantaneous. Since
        we just need an x,y,h coming out of this and into _approach, we don't care. Also,
        you are free to have a side running TargetFinder and just give us the best result
        here. If you return None, we stop. """
        self.log("Calling target_pos_callback")
        self._target_pos_callback().addCallback(self._approach).addErrback(log.err)

    def _approach(self, result_xyh):
        """
        Do a single movement towards the target location given by target_pos_callback
        """
        if self.stopped: return

        if self._actions.isMotionInProgress():
            self.log("WARNING: motion still in progress, waiting for original onDone")
            return

        if result_xyh is None:
            self.log("Done")
            self.stop()
            return

        x, y, h = result_xyh # TODO - take heading into account..

        self.log("Step: %3.2f, %3.2f, %3.2f" % (x, y, h))

        self._movement_callback(delta_x=x, delta_y=y, delta_theta=h).onDone(self._getTargetPos)

################################################################################
def kickerMovementFromRelativeTarget(x, y, h):
    """ Temporary - this is the kicker strategy, here as a reference. We'll start
    out with the much simpler 'just use changeLocationRelative' strategy.

    decide any carry out the best way to reach x,y,h change. Simplest
    is just doing a changeLocationRelative, but possibly we want to do Sideways
    or Turns otherwise - that's what BallKicker does.
    """
    from burst.behavior_params import (calcTargetXY,
        # Area types (where is the ball, err, target, in relation to me)
        BALL_IN_KICKING_AREA, BALL_FRONT_NEAR, BALL_FRONT_FAR, BALL_BETWEEN_LEGS, BALL_SIDE_NEAR,
        BALL_DIAGONAL, BALL_SIDE_NEAR, BALL_SIDE_FAR,
        # Other stuff
        MOVEMENT_PERCENTAGE_TURN, MOVEMENT_PERCENTAGE_FORWARD, MOVEMENT_PERCENTAGE_SIDEWAYS,
        # Movement types (for logging)
        MOVE_FORWARD, MOVE_SIDEWAYS, MOVE_TURN
        )

    (side, kp_x, kp_y, kp_dist, kp_bearing, target_location,
            kick_side_offset) = calcTargetXY(x, y) # TODO - we use calcTargetXY, but ignore the kp_x, kp_y

    ### DECIDE ON NEXT MOVEMENT ###
    # TODO? - remove BALL language and change to TARGET language?
    # Use circle-strafing when near ball (TODO: area for strafing different from kicking-area)
    if target_location == BALL_IN_KICKING_AREA:
        return None

    def move_forward(target_location):
        return (self._actions.changeLocationRelative(x), MOVE_FORWARD)
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
            0.0, y, walk=walks.SIDESTEP_WALK), MOVE_SIDEWAYS)

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
    if target_location in action_selection:
        bd, movement_type = action_selection[target_location](target_location)
    return bd
    #self.log(type_to_msg.get(movement_type, "!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR!!! target location problematic!"))


################################################################################

def getTargetPosition(actions, world_x, world_y, world_heading, close_enough=50, heading_enough=0.1):
    """ calculate relative position given world target position
    and (implicitly) current robot world location.

    close_enough - distance that is good enough (returns None in that case) [cm]

    TODO: look at accuracy of world position of robot (throw error? - print something, since we shouldn't
    be here in that case.
    TODO: factor out the math to burst_util or burst_numpy_util
    TODO: test the math.
    """
    robot = actions._world.robot
    our_x, our_y, our_heading = robot.world_x, robot.world_y, robot.world_heading
    dx, dy, dh = world_x - our_x, world_y - our_y, world_heading - our_heading
    sh, ch = sin(dh), cos(dh)
    rel_x, rel_y = dx * ch - dy * ch, dx * sh + dy * ch # TODO - check me
    dist2 = rel_x**2 + rel_y**2
    if dist2 <= close_enough**2:
        print "approacher.getTargetPosition: close enough (%3.2f <= %3.2f)" % (sqrt(dist2), close_enough)
        return None
    print "approacher.getTargetPosition: %s->%s, rel=(%3.2f,%3.2f) delta=(%3.2f, %3.2f, h %3.2f)" % (
        '%2.3f,%2.3f,h%2.3f' % (our_x, our_y, our_heading),
        '%2.3f,%2.3f,h%2.3f' % (world_x, world_y, world_heading), rel_x, rel_y, dx, dy, our_heading)
    return rel_x, rel_y, dh

def TurtleTurn(actions, x, y, heading, steps):
    """ Educational example, not actually useful.
    
    Equivalent roughly to the following python:
    (assuming x,y -> r, theta in polar coordinates)
    for i in xrange(steps):
        forward(r)
        right(theta)
    or logo:
    repeat steps: [fd r rt theta]
    
    How to use:
    >>> ApproachXY(actions, 100, 0, 3).onDone(pr("I'm done walking in circles!"))
    
    """
    remaining = [steps]
    def target_pos_callback():
        if remaining[0] <= 0:
            return None # signals stopping
        else:
            remaining[0] -= 1
            return x, y, heading
    return Approacher(actions, lambda: succeed(target_pos_callback()))

def ApproachXYHActiveLocalization(actions, x, y, h):
    approacher = Approacher(actions, lambda: actions.localize().getDeferred().addCallback(
        lambda _: getTargetPosition(actions, x, y, h)))
    approacher.target_world_x = x
    approacher.target_world_y = y
    approacher.target_world_h = h
    return approacher

def ApproachTarget(actions, target):
    # TODO - I think this doesn't stop right. Should really do the Behavior thing
    # to make sure stop cleans up.
    def getTargetPosition(_):
        print target.bearing, target.dist
        bearing, dist = target.bearing, target.dist
        return polar2cart(dist, bearing)
    return Approacher(actions, lambda: actions.search([target]).getDeferred().addCallback(getTargetPosition))

def ApproachTargetWithFinder(actions, target):
    # TODO - I think this doesn't stop right. Should really do the Behavior thing
    # to make sure stop cleans up.
    def getTargetPosition(_):
        bearing, dist = target.bearing, target.dist
        return polar2cart(dist, bearing)
    targetFinder = TargetFinder([target])
    approacher = Approacher(actions,
        lambda: actions.search([target]).getDeferred().addCallback(
            getTargetPosition))
    approacher.onDone(targetFinder.stop()) # first onDone, so will be called first.
    return approacher

