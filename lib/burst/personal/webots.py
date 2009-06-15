""" Personal file for webots

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

# 
#from .walks import STRAIGHT_WALK
#STRAIGHT_WALK.defaultSpeed = 100

## Walks

#import burst.moves.walks as walks
#walks.STRAIGHT_WALK.defaultSpeed = 100

import burst.behavior_params as params
params.KICK_X_MIN[:] = [18.0,18.0] #[30.0,30.0]
params.KICK_X_MAX[:] = [21.5,21.5] #[33.0,33.0]
params.KICK_Y_MIN[:] = [4.0,-4.0] #[6.0,-6.0]
params.KICK_Y_MAX[:] = [7.5,-7.5] #[12.5,-12.5]
params.MOVEMENT_PERCENTAGE = 0.55

import burst.actions.actionconsts as actionconsts
actionconsts.DEFAULT_STEPS_FOR_TURN = 60
actionconsts.DEFAULT_SLOW_WALK_STEPS = 60

from burst_consts import DEG_TO_RAD
from .. import walkparameters; WalkParameters = walkparameters.WalkParameters
import burst.moves.walks as walks
walks.STRAIGHT_WALK[:] = walks.Walk(WalkParameters([
           100.0 * DEG_TO_RAD, # 0 ShoulderMedian
           10.0 * DEG_TO_RAD,    # 1 ShoulderAmplitude
           30.0 * DEG_TO_RAD,    # 2 ElbowMedian 
           10.0 * DEG_TO_RAD,    # 3 ElbowAmplitude 
           2.5,                  # 4 LHipRoll(degrees) 
           -2.5,                 # 5 RHipRoll(degrees)
           0.23,                 # 6 HipHeight(meters)
           3.0,                  # 7 TorsoYOrientation(degrees)
           0.07,                 # 8 StepLength
           0.042,                 # 9 StepHeight
           0.06,                 # 10 StepSide (was 0.02)
           0.3,                  # 11 MaxTurn
           0.015,                # 12 ZmpOffsetX
           0.018]),                # 13 ZmpOffsetY 
           18)                  # 14 20ms count per step
