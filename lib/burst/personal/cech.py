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


import burst.moves.walks as walks

walks.STRAIGHT_WALK = walks.Walk('STRAIGHT_WALK', walks.WalkParameters([
           100.0 * walks.DEG_TO_RAD, # ShoulderMedian
           20.0 * walks.DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * walks.DEG_TO_RAD,  # ElbowMedian
           20.0 * walks.DEG_TO_RAD,  # ElbowAmplitude
           3.3,                   # LHipRoll(degrees)
           -5,                  # RHipRoll(degrees)
           0.19,                  # HipHeight(meters)
           -5.5,                   # TorsoYOrientation(degrees) - stopped adjusting to the negative direction - there is a possibility that a little bit more negative is better
           0.05,                  # StepLength
           0.014,                  # StepHeight
           0.04,                  # StepSide
           0.3,                   # MaxTurn
           0.013,                  # ZmpOffsetX
           0.015]),                  # ZmpOffsetY
           25          # 20ms count per step
    )


#walks.TURN_WALK = walks.Walk('TURN_WALK', walks.WalkParameters([
#           100.0 * walks.DEG_TO_RAD, # ShoulderMedian
#           20.0 * walks.DEG_TO_RAD,  # ShoulderAmplitude
#           30.0 * walks.DEG_TO_RAD,  # ElbowMedian
#           20.0 * walks.DEG_TO_RAD,  # ElbowAmplitude
#           5,                   # LHipRoll(degrees)
#           -5,                  # RHipRoll(degrees)
#           0.22,                  # HipHeight(meters) (0.19 isn't good)
#           +8.0,                   # TorsoYOrientation(degrees)
#           0.055,                  # StepLength
#           0.015,                  # StepHeight
#           0.04,                  # StepSide
#           0.3,                   # MaxTurn
#           0.01,                  # ZmpOffsetX
#           0.00]),                  # ZmpOffsetY
#           50          # 20ms count per step
#    )

