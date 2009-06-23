""" Personal file for a robot by the name of this file. """
from .. import walkparameters; WalkParameters = walkparameters.WalkParameters
import burst.moves.walks as walks
from burst_consts import DEG_TO_RAD

walks.FIRST_TWO_SLOW_STEPS = False
walks.STRAIGHT_WALK = walks.Walk(WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           20.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian
           20.0 * DEG_TO_RAD,  # ElbowAmplitude
           5,                   # LHipRoll(degrees)
           -5,                  # RHipRoll(degrees)
           0.19,                  # HipHeight(meters)
           -4.0,                   # TorsoYOrientation(degrees) - stopped adjusting to the negative direction - there is a possibility that a little bit more negative is better
           0.055,                  # StepLength
           0.015,                  # StepHeight
           0.02,                  # StepSide
           0.3,                   # MaxTurn
           0.013,                  # ZmpOffsetX
           0.015]),                  # ZmpOffsetY
           25          # 20ms count per step
    )


#STRAIGHT_WALK.defaultSpeed = 80

import burst.behavior_params as params
params.KICK_X_MIN = [14,14]
params.KICK_X_MAX = [18,18]
params.KICK_Y_MIN = [4.0,-2.5]
params.KICK_Y_MAX = [6.0,-4.5]
