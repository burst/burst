""" Personal file for a robot by the name of this file. """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [12,12]
params.KICK_X_MAX = [18,18]
params.KICK_Y_MIN = [3.5,-1.5]
params.KICK_Y_MAX = [9.5,-8.5]

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

#walks.STRAIGHT_WALK.defaultSpeed = 100 # Eran: 80 seems to fall within ~40cm when running kicker, need to check 100 (150 works for sure)
#walks.SIDESTEP_WALK.defaultSpeed = 20 # 20 seems just fine
