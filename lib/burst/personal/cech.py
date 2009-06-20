""" Personal file for a robot by the name of this file. """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [14.0, 14.0]
params.KICK_X_MAX = [20.0, 20.0]
params.KICK_Y_MIN = [2.0, -3.5]
params.KICK_Y_MAX = [5.0, -6.5]

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

#walks.STRAIGHT_WALK.defaultSpeed = 25



"""
@chorwrap
def CIRCLE_STRAFE_CLOCKWISE():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.00000), float(-0.09250), float(-0.11868), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipRoll")
    angles.append([float(-0.08727), float(0.00698), float(0.00698), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.01745), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180), float(0.26180), float(0.26180), float(0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHand")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.08727), float(-0.10996), float(-0.10996), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipRoll")
    angles.append([float(-0.00873), float(-0.2), float(-0.13962), float(0.00000), float(0.00000)]) # cech 16cm
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])
    return jointCodes, angles, times


@chorwrap
def CIRCLE_STRAFE_COUNTER_CLOCKWISE():
    jointCodes = list()
    angles = list()
    times = list()
    suspend = 1.20000    

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)]) 
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)]) 
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.00000), float(-0.09250), float(-0.11868), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.08727), float(-0.00698), float(-0.00698), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.01745), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHand")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.08727), float(-0.10996), float(-0.10996), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.00873), float(0.16), float(0.13962), float(0.00000), float(0.00000)]) # cech elipse ...
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180), float(0.26180), float(0.26180), float(0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])
    return jointCodes, angles, times
"""

