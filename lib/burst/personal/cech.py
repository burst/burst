""" Personal file for a robot by the name of this file. """

## Behavior params - when ball between legs (touching both feet), X=14, Y=-1.7
import burst.behavior_params as params
params.KICK_X_MIN = [14.0, 14.0]
params.KICK_X_MAX = [20.0, 20.0]
#params.KICK_Y_MIN = [3.5, -4.5]
#params.KICK_Y_MAX = [6.5, -7.5]
params.KICK_Y_MIN = [3.65, -4.5]
params.KICK_Y_MAX = [6.65, -7.5]



## Choreograph moves
import burst.moves.choreograph as choreograph
(jointCodes, angles, times) = choreograph.CIRCLE_STRAFE_CLOCKWISE
angles[jointCodes.index("RHipRoll")][1] = -0.2
(jointCodes, angles, times) = choreograph.CIRCLE_STRAFE_COUNTER_CLOCKWISE
angles[jointCodes.index("LHipRoll")][1] = 0.16
