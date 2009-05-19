# started out as a translation of corpus/Kinematics.h
# with the ultimate goal of transforming vision x and y and object width
# using joint angles and accelerometer inclination angles into
# local coordinates (bearing and distance) to be fed into the
# localization module, at first step to check the localization of northern
# since I suspect they don't use the pitch correctly.

import numpy
import math
from numpy import sin, cos

TO_RAD = math.pi/180.0
M_PI_FLOAT = math.pi

X_AXIS, Y_AXIS, Z_AXIS, W_AXIS = 0, 1, 2, 3

def identity():
    return numpy.matrix(numpy.identity(4))

def translation4D(dx, dy, dz):
    m = identity()
    m[X_AXIS,W_AXIS] = dx
    m[Y_AXIS,W_AXIS] = dy
    m[Z_AXIS,W_AXIS] = dz
    return m

def rotation4D(axis, angle):
    rot = identity()
    sinAngle = sin(angle)
    cosAngle = cos(angle)
    if angle == 0.0:
        return rot;
    if axis == X_AXIS:
        rot[Y_AXIS, Y_AXIS] =  cosAngle
        rot[Y_AXIS, Z_AXIS] = -sinAngle
        rot[Z_AXIS, Y_AXIS] =  sinAngle
        rot[Z_AXIS, Z_AXIS] =  cosAngle
    elif axis == Y_AXIS:
        rot[X_AXIS, X_AXIS] =  cosAngle
        rot[X_AXIS, Z_AXIS] =  sinAngle
        rot[Z_AXIS, X_AXIS] = -sinAngle
        rot[Z_AXIS, Z_AXIS] =  cosAngle
    elif axis == Z_AXIS:
        rot[X_AXIS, X_AXIS] =  cosAngle
        rot[X_AXIS, Y_AXIS] = -sinAngle
        rot[Y_AXIS, X_AXIS] =  sinAngle
        rot[Y_AXIS, Y_AXIS] =  cosAngle
    return rot

def calculateForwardTransform(id, angles):
    """
    id - chain id
    angles - [float]
    """
    fullTransform = identity()

    # Do base transforms
    for baseTransform in BASE_TRANSFORMS[id]:
      fullTransform = fullTransform * baseTransform

    # Do mDH transforms
    numTransforms = NUM_JOINTS_CHAIN[id]
    for angle, (alpha, l, theta, d) in zip(angles, MDH_PARAMS[id]):
        # Right before we do a transformation, we are in the correct
        # coordinate frame and we need to store it, so we know where all the
        # links of a chain are. We only need to do this if the transformation
        # gives us a new link

        #length L - movement along the X(i-1) axis
        if l != 0:
            transX = translation4D(l,0.0,0.0)
            fullTransform = fullTransform * transX

        #twist: - rotate about the X(i-1) axis
        if alpha != 0:
            rotX = rotation4D(X_AXIS, alpha)
            fullTransform = fullTransform * rotX
      
        #theta - rotate about the Z(i) axis
        if theta + angle != 0:
            rotZ = rotation4D(Z_AXIS, theta + angle)
            fullTransform = fullTransform * rotZ
      
        #offset D movement along the Z(i) axis
        if d != 0:
            transZ = translation4D(0.0, 0.0, d)
            fullTransform = fullTransform * transZ
      
    # Do the end transforms
    for endTransform in END_TRANSFORMS[id]:
      fullTransform = fullTransform * endTransform
    
    return fullTransform

SHOULDER_OFFSET_Y = 98.0
UPPER_ARM_LENGTH = 90.0
LOWER_ARM_LENGTH = 145.0
SHOULDER_OFFSET_Z = 100.0
THIGH_LENGTH = 100.0
TIBIA_LENGTH = 100.0
NECK_OFFSET_Z = 126.5
HIP_OFFSET_Y = 50.0
HIP_OFFSET_Z = 85.0
FOOT_HEIGHT = 46.0

# Bottom Camera
CAMERA_OFF_X = 48.80 # in millimeters
CAMERA_OFF_Z = 23.81  # in millimeters
CAMERA_PITCH_ANGLE = 40.0 * TO_RAD # 40 degrees

#*********       Joint Bounds       ***********/
HEAD_BOUNDS = [[-2.09,2.09],[-.785,.785]]

# Order of arm joints: ShoulderPitch, SRoll, ElbowYaw, ERoll
LEFT_ARM_BOUNDS = [[-2.09,2.09],
    [0.0,1.65],
    [-2.09,2.09],
    [-1.57,0.0]
    ,[-1.832, 1.832],
        [0.0, 0.0]
]
RIGHT_ARM_BOUNDS = [[-2.09,2.09],
    [-1.65,0.0],
    [-2.09,2.09],
    [0.0,1.57]
    ,[-1.832, 1.832],
        [0.0, 0.0]
]

# Order of leg joints: HYPitch HipPitch HipRoll KneePitch APitch ARoll
LEFT_LEG_BOUNDS = [[-1.57,0.0],
    [-1.57,.436],
    [-.349,.785],
    [0.0,2.269],
    [-1.309,.524],
    [-.785,.349]
]
RIGHT_LEG_BOUNDS = [[-1.57,0.0],
    [-1.57,.436],
    [-.785,.349],
    [0.0,2.269],
    [-1.309,.524],
    [-.349,.785]]

#*********     joint velocity limits **********/
#Set hardware values- nominal speed in rad/20ms
#from $AL_DIR/doc/reddoc
#M=motor r = reduction ratio

M1R1_NOMINAL = 0.0658
M1R2_NOMINAL = 0.1012
M2R1_NOMINAL = 0.1227
M2R2_NOMINAL = 0.1065

M1R1_NO_LOAD = 0.08308
M1R2_NO_LOAD = 0.1279
M2R1_NO_LOAD = 0.16528
M2R2_NO_LOAD = 0.1438

M1R1_AVG = (M1R1_NOMINAL + M1R1_NO_LOAD )*0.5
M1R2_AVG = (M1R2_NOMINAL + M1R2_NO_LOAD )*0.5
M2R1_AVG = (M2R1_NOMINAL + M2R1_NO_LOAD )*0.5
M2R2_AVG = (M2R2_NOMINAL + M2R2_NO_LOAD )*0.5

jointsMaxVelNominal = [
#head
    M2R2_NOMINAL, M2R1_NOMINAL,
#left arm
    M2R1_NOMINAL, M2R2_NOMINAL, M2R1_NOMINAL, M2R2_NOMINAL,
    M1R1_NOMINAL, M1R1_NOMINAL,
#left leg
    M1R1_NOMINAL, M1R1_NOMINAL, M1R2_NOMINAL,
    M1R2_NOMINAL, M1R2_NOMINAL, M1R1_NOMINAL,
#right leg
    M1R1_NOMINAL, M1R1_NOMINAL, M1R2_NOMINAL,
    M1R2_NOMINAL, M1R2_NOMINAL, M1R1_NOMINAL,
#right arm
    M2R2_NOMINAL, M2R2_NOMINAL, M2R1_NOMINAL, M2R2_NOMINAL
        ,M1R1_NOMINAL, M1R1_NOMINAL
]

jointsMaxVelNoLoad = [
#head
    M2R2_NO_LOAD, M2R1_NO_LOAD,
#left arm
    M2R1_NO_LOAD, M2R2_NO_LOAD, M2R1_NO_LOAD, M2R2_NO_LOAD,
    M1R1_NO_LOAD, M1R1_NO_LOAD,
#left leg
    M1R1_NO_LOAD, M1R1_NO_LOAD, M1R2_NO_LOAD,
    M1R2_NO_LOAD, M1R2_NO_LOAD, M1R1_NO_LOAD,
#right leg
    M1R1_NO_LOAD, M1R1_NO_LOAD, M1R2_NO_LOAD,
    M1R2_NO_LOAD, M1R2_NO_LOAD, M1R1_NO_LOAD,
#right arm
    M2R2_NO_LOAD, M2R2_NO_LOAD, M2R1_NO_LOAD, M2R2_NO_LOAD
        ,M1R1_NO_LOAD, M1R1_NO_LOAD
]

jointsMaxVelAvg = [
#head
    M2R2_AVG, M2R1_AVG,
#left arm
    M2R1_AVG, M2R2_AVG, M2R1_AVG, M2R2_AVG,
    M1R1_AVG, M1R1_AVG,
#left leg
    M1R1_AVG, M1R1_AVG, M1R2_AVG,
    M1R2_AVG, M1R2_AVG, M1R1_AVG,
#right leg
    M1R1_AVG, M1R1_AVG, M1R2_AVG,
    M1R2_AVG, M1R2_AVG, M1R1_AVG,
#right arm
    M2R2_AVG, M2R2_AVG, M2R1_AVG, M2R2_AVG
        ,M1R1_AVG, M1R1_AVG
]


#*********      mDH parameters      ***********/

#mDHNames
ALPHA, L, THETA, D = 0, 1, 2, 3

#                                  (alpha,  a ,  theta ,   d  )
HEAD_MDH_PARAMS = [[0.0 , 0.0,  0.0 , 0.0],
    [-M_PI_FLOAT/2, 0.0, -M_PI_FLOAT/2 , 0.0]]

LEFT_ARM_MDH_PARAMS = [[-M_PI_FLOAT/2,0.0,0.0,0.0],
    [ M_PI_FLOAT/2,0.0,M_PI_FLOAT/2,0.0],
    [ M_PI_FLOAT/2,0.0,0.0,UPPER_ARM_LENGTH],
    [-M_PI_FLOAT/2,0.0,0.0,0.0]]

LEFT_LEG_MDH_PARAMS = [[ -3*M_PI_FLOAT/4, 0.0,  -M_PI_FLOAT/2, 0.0],
    [ -M_PI_FLOAT/2,   0.0,   M_PI_FLOAT/4, 0.0],
    [ M_PI_FLOAT/2,    0.0,     0.0, 0.0],
#[ M_PI_FLOAT/2,-THIGH_LENGTH,0.0, 0.0],
    [   0.0,-THIGH_LENGTH,0.0, 0.0],
    [   0.0,-TIBIA_LENGTH,0.0, 0.0],
    [-M_PI_FLOAT/2,    0.0,     0.0, 0.0]]

RIGHT_LEG_MDH_PARAMS= [[ -M_PI_FLOAT/4,  0.0,   -M_PI_FLOAT/2, 0.0],
    [ -M_PI_FLOAT/2,   0.0,  -M_PI_FLOAT/4, 0.0],
    [  M_PI_FLOAT/2,    0.0,    0.0, 0.0],
#[  M_PI_FLOAT/2,-THIGH_LENGTH,0.0,0.0],
    [ 0.0,-THIGH_LENGTH,0.0, 0.0],
    [0.0,-TIBIA_LENGTH,0.0,0.0],
    [-M_PI_FLOAT/2,0.0,0.0,0.0]]

RIGHT_ARM_MDH_PARAMS = [[-M_PI_FLOAT/2, 0.0,0.0,0.0],
    [ M_PI_FLOAT/2, 0.0,M_PI_FLOAT/2,0.0],
    [ M_PI_FLOAT/2, 0.0,0.0,UPPER_ARM_LENGTH],
    [-M_PI_FLOAT/2, 0.0,0.0,0.0]]

MDH_PARAMS = [
    HEAD_MDH_PARAMS,
    LEFT_ARM_MDH_PARAMS,
    LEFT_LEG_MDH_PARAMS,
    RIGHT_LEG_MDH_PARAMS,
    RIGHT_ARM_MDH_PARAMS
]

#Base transforms to get from body center to beg. of chain
HEAD_BASE_TRANSFORMS = [
    translation4D( 0.0,
        0.0,
        NECK_OFFSET_Z )]

LEFT_ARM_BASE_TRANSFORMS = [
    translation4D( 0.0,
        SHOULDER_OFFSET_Y,
        SHOULDER_OFFSET_Z ) ]

LEFT_LEG_BASE_TRANSFORMS = [
    translation4D( 0.0,
        HIP_OFFSET_Y,
        -HIP_OFFSET_Z ) ]

RIGHT_LEG_BASE_TRANSFORMS = [
    translation4D( 0.0,
        -HIP_OFFSET_Y,
        -HIP_OFFSET_Z ) ]

RIGHT_ARM_BASE_TRANSFORMS = [
    translation4D( 0.0,
        -SHOULDER_OFFSET_Y,
        SHOULDER_OFFSET_Z ) ]

BASE_TRANSFORMS = [
    HEAD_BASE_TRANSFORMS,
    LEFT_ARM_BASE_TRANSFORMS,
    LEFT_LEG_BASE_TRANSFORMS,
    RIGHT_LEG_BASE_TRANSFORMS,
    RIGHT_ARM_BASE_TRANSFORMS ]

#Base transforms to get from body center to beg. of chain
HEAD_END_TRANSFORMS = [
    rotation4D(X_AXIS, M_PI_FLOAT/2),
    rotation4D(Y_AXIS,M_PI_FLOAT/2),
    translation4D(CAMERA_OFF_X, 0, CAMERA_OFF_Z),
    rotation4D(Y_AXIS, CAMERA_PITCH_ANGLE) ]

LEFT_ARM_END_TRANSFORMS = [
    rotation4D(Z_AXIS, -M_PI_FLOAT/2),
    translation4D(LOWER_ARM_LENGTH,0.0,0.0) ]

LEFT_LEG_END_TRANSFORMS = [
    rotation4D(Z_AXIS, M_PI_FLOAT),
    rotation4D(Y_AXIS, -M_PI_FLOAT/2),
    translation4D(0.0,
                  0.0,
                  -FOOT_HEIGHT) ]

RIGHT_LEG_END_TRANSFORMS = [
    rotation4D(Z_AXIS, M_PI_FLOAT),
    rotation4D(Y_AXIS, -M_PI_FLOAT/2),
    translation4D(0.0,
                  0.0,
                  -FOOT_HEIGHT) ]

RIGHT_ARM_END_TRANSFORMS = [
    rotation4D(Z_AXIS, -M_PI_FLOAT/2),
    translation4D(LOWER_ARM_LENGTH,0.0,0.0) ]


END_TRANSFORMS = [
    HEAD_END_TRANSFORMS,
    LEFT_ARM_END_TRANSFORMS,
    LEFT_LEG_END_TRANSFORMS,
    RIGHT_LEG_END_TRANSFORMS,
    RIGHT_ARM_END_TRANSFORMS ]

NUM_BASE_TRANSFORMS = [1,1,1,1,1]
NUM_END_TRANSFORMS = [4,2,3,3,2]
NUM_JOINTS_CHAIN = [2,4,6,6,4]

