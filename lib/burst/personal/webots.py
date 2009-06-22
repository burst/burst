""" Personal file for webots """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [17.5,17.5] #[30.0,30.0]
params.KICK_X_MAX = [21.0,21.0] #[33.0,33.0]
params.KICK_Y_MIN = [4.0,-4.0] #[6.0,-6.0]
params.KICK_Y_MAX = [10.0,-10.0] #[12.5,-12.5]
params.MOVEMENT_PERCENTAGE_FORWARD = 0.55
params.MOVEMENT_PERCENTAGE_SIDEWAYS = 0.9
params.MOVEMENT_PERCENTAGE_TURN = 0.9


## General moves
import burst.moves.poses as poses
poses.STRAIGHT_WALK_INITIAL_POSE = [
    ((1.734912, 0.25460203999999997, -1.563188, -0.52918803999999997), 
    (-0.010696038999999999, -0.088930041000000001, -0.65957807999999996, 1.5416281000000001, -0.76857597, 0.078275964000000003), 
    (-0.010696038999999999, 0.0061779618000000003, -0.66272998000000005, 1.5432459999999999, -0.78229808999999995, -0.0030260384000000001), 
    (1.747268, -0.27309397000000002, 1.5661721, 0.50626194000000002),
    1.0)]

## Walks
from .. import walkparameters; WalkParameters = walkparameters.WalkParameters
import burst.moves.walks as walks
from burst_consts import DEG_TO_RAD

walks.FIRST_TWO_SLOW_STEPS = False
walks.STRAIGHT_WALK = walks.Walk(WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           20.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           20.0 * DEG_TO_RAD,  # ElbowAmplitude 
           5.5,                   # LHipRoll(degrees) 
           -5.5,                  # RHipRoll(degrees)
           0.19,                  # HipHeight(meters)
           -4.0,                   # TorsoYOrientation(degrees) - stopped adjusting to the negative direction - there is a possibility that a little bit more negative is better
           0.055,                  # StepLength
           0.015,                  # StepHeight
           0.02,                  # StepSide
           0.3,                   # MaxTurn
           0.013,                  # ZmpOffsetX
           0.015]),                  # ZmpOffsetY
           25)                  # 20ms count per step


import burst.actions.actionconsts as actionconsts
actionconsts.DEFAULT_STEPS_FOR_TURN = 60
