""" Personal file for a robot by the name of this file. """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [14.0, 14.0]
params.KICK_X_MAX = [20.0, 20.0]
params.KICK_Y_MIN = [2.0, -3.5]
params.KICK_Y_MAX = [5.0, -6.5]

## Choreograph moves
import burst.moves.choreograph as choreograph
(jointCodes, angles, times) = choreograph.CIRCLE_STRAFE_CLOCKWISE
angles[jointCodes.index("RHipRoll")] = -0.2
(jointCodes, angles, times) = choreograph.CIRCLE_STRAFE_COUNTER_CLOCKWISE
angles[jointCodes.index("LHipRoll")] = 0.16
