from math import pi

import burst
from burst_util import chainDeferreds, shortest_angle
from burst.walkparameters import WalkParameters
from burst.actions.actionconsts import (MINIMAL_CHANGELOCATION_TURN, DEFAULT_STEPS_FOR_TURN, DEFAULT_SLOW_WALK_STEPS)
from burst_events import EVENT_CHANGE_LOCATION_DONE
from burst_consts import SUPPORT_MODE_DOUBLE_LEFT
from burst.world import World
import burst.moves.walks as walks

class Journey(object):

    """ Class used by changeLocationRelative. Breaks down a single walk
    into multiple legs. In the simplest case it acts like the old changeLocationRelative,
    i.e. does a single leg.

    The extra complication arises from doing everything in deferred mode - every call to
    a proxy is chained via addCallback.
    """

    SLOW_START_STEPS = 2 # The amount of steps one should take at a slower pace at the beginning.

    def __init__(self, actions):
        self.verbose = burst.options.verbose_journey
        self._printQueueBeforeExecution = True
        self._actions = actions
        self._world = self._actions._world
        self._motion = self._actions._motion
        self._deferred = None
        self._distance, self._bearing, self._delta_theta = None, None, None
        self._turn = [None, None]
        self._distance_left = None
        self._time_per_steps, self._step_length = None, None
        self._make_bd = self._world.burst_deferred_maker.make

    def __str__(self):
        return "<Journey %3.3f distance, %3.3f bearing>" % (self._distance, self._bearing)

    def start(self, walk, steps_before_full_stop,
            distance, bearing, delta_theta):
        """ Do first leg, if the distance is smaller than threshold do final
        leg, otherwise schedule the next leg """
        self._cmds = [] # See comment on _addCommand
        self._deferred = self._make_bd(None)
        self._distance = distance
        self._bearing = bearing
        self._delta_theta = delta_theta
        self._distance_left = self._distance
        self._turn = turn = [None, None] # for duration estimation
        #import pdb; pdb.set_trace()
        self._time_per_steps = walk.defaultSpeed
        self._step_length = step_length = walk[WalkParameters.StepLength]
        if steps_before_full_stop == 0:
            self._leg_distance = self._distance
        else:
            self._leg_distance = steps_before_full_stop * step_length
        if abs(bearing) >= MINIMAL_CHANGELOCATION_TURN:
            turn[0] = bearing
        final_turn = delta_theta - bearing
        if abs(final_turn) >= MINIMAL_CHANGELOCATION_TURN:
            turn[1] = final_turn
        # TODO - compute duration correctly for the multiple legs
        self._duration = duration = (self._time_per_steps * distance / step_length +
                    (turn[0] and DEFAULT_STEPS_FOR_TURN or self._actions._eventmanager.dt) ) * 0.02 # 20ms steps

        self._addCommand("walkconfig", lambda _: self._actions.setWalkConfig(walk.walkParameters))
        self._addCommand("support mode", lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))

        if self.verbose:
            if turn[0]:
                print "Journey: Planned: addTurn %3.3f" % turn[0]
            print "Journey: Planned: Straight walk: StepLength: %3.3f distance: %3.3f est. duration: %3.3f" % (
                step_length, distance, duration)
            if turn[1]:
                print "Journey: Planned: addTurn %3.3f" % turn[1]

        # Avoid turns
        if self._turn[0]:
            self._addTurn(self._turn[0])

        self.onLegComplete()

        return self._deferred

    def _addTurn(self, ang):
        ang = shortest_angle(ang)
        self._addCommand("%s %3.3f" % ((ang >= 0.0 or ang <=-pi) and 'lt' or 'rt' , ang),
            lambda _: self._motion.addTurn(ang, DEFAULT_STEPS_FOR_TURN))

    def _addCommand(self, description, f):
        """
        we collect any call to a proxy here, for easy understanding
        since we will want to chain them (make their execution sequential)
        without resorting to breaking everything into callbacks due to the slightly
        complex nature of this function
        """
        self._cmds.append((description, f))

    def _executeAllCommands(self):
        if self._printQueueBeforeExecution and len(self._cmds) > 4: # 3 - walkconfig, support, single leg (slow+regular walk).
            print "Executing Journey Queue: %s" % ('; '.join(desc for desc, f in self._cmds))
        d = chainDeferreds([f for desc, f in self._cmds])
        self._cmds = []
        return d

    def lastLeg(self):
        # Now turn to the final angle, taking into account the turn we
        # already did
        self.addSingleLeg()
        if self._turn[1]:
            self._addTurn(self._turn[1])
        last_leg_duration = 1.0 # TODO - duration calculation for real
        self._world._movecoordinator.walk(d=self._executeAllCommands(),
            duration=last_leg_duration,
            description=('journey last leg', self._distance, self._bearing, self._delta_theta)
                ).onDone(self.callbackAndReset)

    def callbackAndReset(self):
        # TODO: do I need to reset anything?
        self._deferred.callOnDone()

    def onLegComplete(self):
        if self._distance_left <= self._leg_distance:
            self.lastLeg()
        else:
            self.addSingleLeg()
            leg_duration = 1.0 # TODO - compute duration correctly
            self._world._movecoordinator.walk(d=self._executeAllCommands(),
                duration=leg_duration,
                description='journey mid leg').onDone(self.onLegComplete)

    def _addWalkStraight(self, desc_tmpl, dist, steps):
        self._addCommand(desc_tmpl % dist, lambda _: self._motion.addWalkStraight(dist, steps))

    def addSingleLeg(self):
        """ call _motion.addWalkStraight, for webots walk do a single type of walk,
        for real robot do a slow walk for SLOW_START_STEPS and then a normal walk
        """
        leg_distance = min(self._leg_distance, self._distance_left)

        if walks.FIRST_TWO_SLOW_STEPS and World.connected_to_nao:
            slow_walk_distance = min(leg_distance, self._step_length * self.SLOW_START_STEPS)
            normal_walk_distance = leg_distance - slow_walk_distance
            self._addWalkStraight( "slow fd %3.2f", slow_walk_distance, DEFAULT_SLOW_WALK_STEPS )
            self._addWalkStraight( "normal fd %3.2f", normal_walk_distance, self._time_per_steps)
        else:
            self._addWalkStraight( "fd %3.2f", leg_distance, self._time_per_steps )

        self._distance_left -= leg_distance
        if self._distance_left < 0.0:
            print "ERROR: Journey distance left calculation incorrect"
            import pdb; pdb.set_trace()
            self._distance_left = 0.0

