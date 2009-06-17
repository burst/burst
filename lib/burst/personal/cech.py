""" Personal file for a robot by the name of this file.

PLEASE PAY ATTENTION TO THE FOLLOWING:

There is the good way to update stuff, and the bad way (asaf, I'm looking at you).

# BAD
import moves.walks as walks
walks.SIT_POS = [2,3,4]

# GOOD
import moves.walks as walks
walks.SIT_POS[:] = [2,3,4]

# ALSO GOOD
walks.SIT_POS[2] = 10

"""

## General moves
#import burst.moves.general_moves as general_moves
#general_moves.SIT_POS[:] = [
#           ((0.,90.,0.,0.),
#            (-12.5, -5., -42.5, 125., -70., 6.),
#            (-12.5, 5., -42.5, 125., -70., -6.),
#            (0.,-90.,0.,0.),3.0),
#           ((55.,7.,0.,-30.),
#            (-12.5, -5., -42.5, 125., -70., 6.),
#            (-12.5, 5., -42.5, 125., -70., -6.),
#            (55.,-7.,0.,30.),1.5)]

## Walks
from .. import walkparameters; WalkParameters = walkparameters.WalkParameters
import burst.moves.walks as walks
#walks.STRAIGHT_WALK.defaultSpeed = 25

walks.STRAIGHT_WALK = Walk(WalkParameters([
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



## Behavior params

import burst.behavior_params as params
params.KICK_X_MIN[:] = [14.0, 14.0]
params.KICK_X_MAX[:] = [20.0, 20.0]
params.KICK_Y_MIN[:] = [2.0, -3.5]
params.KICK_Y_MAX[:] = [5.0, -6.5]
