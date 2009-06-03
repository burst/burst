"""
This file must include any constant that is not personal to any robot, and
doesn't change during the life of the program. (i.e., constant).

For instance, don't put any moves in here, or any parameters that are personal.
"""

import os # for HOME

import math
from math import tan

# Operating Environment constants
ROBOT_IP_TO_NAME = {
    '192.168.5.126'	: 'messi',
    '192.168.5.170'	: 'gerrard',
    '192.168.5.226'	: 'cech',
    '192.168.5.168'	: 'hagi',
    '192.168.5.224'	: 'raul',
    '192.168.5.228'	: 'maldini',
}

# Proxy names
BURST_SHARED_MEMORY_PROXY_NAME = "burstmem"
BURST_RECORDER_PROXY_NAME = "recorder"

# Naoqi Constants

BALANCE_MODE_OFF = 0
BALANCE_MODE_AUTO = 1
BALANCE_MODE_COM_CONTROL = 2

# Nao Academic Edition (Robocup Edition has 22)
NUM_JOINTS = 26
NUM_ACTUAL_JOINTS = 25 # Just to document, not used anywhere

(HEAD_YAW_JOINT_INDEX, HEAD_PITCH_JOINT_INDEX,
L_SHOULDER_PITCH_JOINT_INDEX, L_SHOULDER_ROLL_JOINT_INDEX,
L_ELBOW_YAW_JOINT_INDEX, L_ELBOW_ROLL_JOINT_INDEX,
L_WRIST_YAW_JOINT_INDEX, L_HAND_JOINT_INDEX,
L_HIP_YAW_PITCH_JOINT_INDEX, L_HIP_ROLL_JOINT_INDEX,
L_HIP_PITCH_JOINT_INDEX, L_KNEE_PITCH_JOINT_INDEX,
L_ANKLE_PITCH_JOINT_INDEX, L_ANKLE_ROLL_JOINT_INDEX,
R_HIP_YAW_PITCH_JOINT_INDEX, R_HIP_ROLR_JOINT_INDEX,
R_HIP_PITCH_JOINT_INDEX, R_KNEE_PITCH_JOINT_INDEX,
R_ANKLE_PITCH_JOINT_INDEX, R_ANKLE_ROLR_JOINT_INDEX,
R_SHOULDER_PITCH_JOINT_INDEX, R_SHOULDER_ROLR_JOINT_INDEX,
R_ELBOW_YAW_JOINT_INDEX, R_ELBOW_ROLR_JOINT_INDEX,
R_WRIST_YAW_JOINT_INDEX, R_HAND_JOINT_INDEX,) = range(NUM_JOINTS)

# support modes
SUPPORT_MODE_LEFT, SUPPORT_MODE_DOUBLE_LEFT, SUPPORT_MODE_RIGHT, SUPPORT_MODE_DOUBLE_RIGHT = 0, 1, 2, 3

INTERPOLATION_LINEAR, INTERPOLATION_SMOOTH = 0, 1

# Math constants

DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi
CM_TO_METER = 100. # yeah, seems stupid, but probably better than using 100 throughout the code...

# Camera / Vision constants

# Image Parameters
FOV_X = 46.4 * DEG_TO_RAD
FOV_Y = 34.8 * DEG_TO_RAD
# image width / height source: OV7670 Datasheet
IMAGE_WIDTH_MM = 2.36
IMAGE_HEIGHT_MM = 1.76
FOCAL_LENGTH_MM = IMAGE_WIDTH_MM/2 / tan(FOV_X/2)

IMAGE_WIDTH = 320.0
IMAGE_HEIGHT = 240.0
IMAGE_HALF_WIDTH = IMAGE_WIDTH / 2
IMAGE_HALF_HEIGHT = IMAGE_HEIGHT / 2

IMAGE_WIDTH_INT = int(IMAGE_WIDTH)
IMAGE_HEIGHT_INT = int(IMAGE_HEIGHT)

MM_TO_PIX_X = IMAGE_WIDTH/IMAGE_WIDTH_MM
MM_TO_PIX_Y = IMAGE_HEIGHT/IMAGE_HEIGHT_MM
PIX_X_TO_MM = 1.0 / MM_TO_PIX_X
PIX_Y_TO_MM = 1.0 / MM_TO_PIX_Y
IMAGE_CENTER_X = (IMAGE_WIDTH  - 1) / 2.0
IMAGE_CENTER_Y = (IMAGE_HEIGHT - 1) / 2.0

PIX_TO_RAD_X = FOV_X / IMAGE_WIDTH
PIX_TO_RAD_Y = FOV_Y / IMAGE_HEIGHT

# Shared memory constants

MMAP_FILENAME           = "/home/root/burst/lib/etc/burstmem.mmap"
MMAP_LENGTH      = 4096

# Event Manager constants
EVENT_MANAGER_DT = 0.05 # seconds

# World constants

MISSING_FRAMES_MINIMUM = 5

MIN_BEARING_CHANGE = 1e-3 # TODO - ?
MIN_DIST_CHANGE = 1e-3

BALL_REAL_DIAMETER = 8.7 # cm
ROBOT_DIAMETER = 58.0    # this is from Appendix A of Getting Started - also, doesn't hands raised into account
GOAL_POST_HEIGHT = 80.0
GOAL_POST_DIAMETER = 80.0 # TODO: name? this isn't the radius*2 of the base, it is the diameter in the sense of longest line across an image of the post.

LEFT = 0
RIGHT = 1
DOWN = 2
UP = 3

# Robot constants
MOTION_FINISHED_MIN_DURATION = EVENT_MANAGER_DT * 3

#############################################################
# Lists of variable names exported by us to ALMemory

# To recreate under pynaoqi run:
#
#   refilter('/BURST/Vision',names)
#
vision_vars = ['/BURST/Vision/BGCrossbar/AngleXDeg',
 '/BURST/Vision/BGCrossbar/AngleYDeg',
 '/BURST/Vision/BGCrossbar/BearingDeg',
 '/BURST/Vision/BGCrossbar/CenterX',
 '/BURST/Vision/BGCrossbar/CenterY',
 '/BURST/Vision/BGCrossbar/Distance',
 '/BURST/Vision/BGCrossbar/ElevationDeg',
 '/BURST/Vision/BGCrossbar/FocDist',
 '/BURST/Vision/BGCrossbar/Height',
 '/BURST/Vision/BGCrossbar/LeftOpening',
 '/BURST/Vision/BGCrossbar/RightOpening',
 '/BURST/Vision/BGCrossbar/Width',
 '/BURST/Vision/BGCrossbar/X',
 '/BURST/Vision/BGCrossbar/Y',
 '/BURST/Vision/BGCrossbar/shotAvailable',
 '/BURST/Vision/BGLP/AngleXDeg',
 '/BURST/Vision/BGLP/AngleYDeg',
 '/BURST/Vision/BGLP/BearingDeg',
 '/BURST/Vision/BGLP/CenterX',
 '/BURST/Vision/BGLP/CenterY',
 '/BURST/Vision/BGLP/Distance',
 '/BURST/Vision/BGLP/DistanceCertainty',
 '/BURST/Vision/BGLP/ElevationDeg',
 '/BURST/Vision/BGLP/FocDist',
 '/BURST/Vision/BGLP/Height',
 '/BURST/Vision/BGLP/IDCertainty',
 '/BURST/Vision/BGLP/Width',
 '/BURST/Vision/BGLP/X',
 '/BURST/Vision/BGLP/Y',
 '/BURST/Vision/BGRP/AngleXDeg',
 '/BURST/Vision/BGRP/AngleYDeg',
 '/BURST/Vision/BGRP/BearingDeg',
 '/BURST/Vision/BGRP/CenterX',
 '/BURST/Vision/BGRP/CenterY',
 '/BURST/Vision/BGRP/Distance',
 '/BURST/Vision/BGRP/DistanceCertainty',
 '/BURST/Vision/BGRP/ElevationDeg',
 '/BURST/Vision/BGRP/FocDist',
 '/BURST/Vision/BGRP/Height',
 '/BURST/Vision/BGRP/IDCertainty',
 '/BURST/Vision/BGRP/Width',
 '/BURST/Vision/BGRP/X',
 '/BURST/Vision/BGRP/Y',
 '/BURST/Vision/Ball/BearingDeg',
 '/BURST/Vision/Ball/CenterX',
 '/BURST/Vision/Ball/CenterY',
 '/BURST/Vision/Ball/Confidence',
 '/BURST/Vision/Ball/Distance',
 '/BURST/Vision/Ball/ElevationDeg',
 '/BURST/Vision/Ball/FocDist',
 '/BURST/Vision/Ball/Height',
 '/BURST/Vision/Ball/Width',
 '/BURST/Vision/YGCrossbar/AngleXDeg',
 '/BURST/Vision/YGCrossbar/AngleYDeg',
 '/BURST/Vision/YGCrossbar/BearingDeg',
 '/BURST/Vision/YGCrossbar/CenterX',
 '/BURST/Vision/YGCrossbar/CenterY',
 '/BURST/Vision/YGCrossbar/Distance',
 '/BURST/Vision/YGCrossbar/ElevationDeg',
 '/BURST/Vision/YGCrossbar/FocDist',
 '/BURST/Vision/YGCrossbar/Height',
 '/BURST/Vision/YGCrossbar/LeftOpening',
 '/BURST/Vision/YGCrossbar/RightOpening',
 '/BURST/Vision/YGCrossbar/Width',
 '/BURST/Vision/YGCrossbar/X',
 '/BURST/Vision/YGCrossbar/Y',
 '/BURST/Vision/YGCrossbar/shotAvailable',
 '/BURST/Vision/YGLP/AngleXDeg',
 '/BURST/Vision/YGLP/AngleYDeg',
 '/BURST/Vision/YGLP/BearingDeg',
 '/BURST/Vision/YGLP/CenterX',
 '/BURST/Vision/YGLP/CenterY',
 '/BURST/Vision/YGLP/Distance',
 '/BURST/Vision/YGLP/DistanceCertainty',
 '/BURST/Vision/YGLP/ElevationDeg',
 '/BURST/Vision/YGLP/FocDist',
 '/BURST/Vision/YGLP/Height',
 '/BURST/Vision/YGLP/IDCertainty',
 '/BURST/Vision/YGLP/Width',
 '/BURST/Vision/YGLP/X',
 '/BURST/Vision/YGLP/Y',
 '/BURST/Vision/YGRP/AngleXDeg',
 '/BURST/Vision/YGRP/AngleYDeg',
 '/BURST/Vision/YGRP/BearingDeg',
 '/BURST/Vision/YGRP/CenterX',
 '/BURST/Vision/YGRP/CenterY',
 '/BURST/Vision/YGRP/Distance',
 '/BURST/Vision/YGRP/DistanceCertainty',
 '/BURST/Vision/YGRP/ElevationDeg',
 '/BURST/Vision/YGRP/FocDist',
 '/BURST/Vision/YGRP/Height',
 '/BURST/Vision/YGRP/IDCertainty',
 '/BURST/Vision/YGRP/Width',
 '/BURST/Vision/YGRP/X',
 '/BURST/Vision/YGRP/Y']

# Joint data
joint_names, joint_limits = (['HeadYaw',
  'HeadPitch',
  'LShoulderPitch',
  'LShoulderRoll',
  'LElbowYaw',
  'LElbowRoll',
  'LWristYaw',
  'LHand',
  'LHipYawPitch',
  'LHipRoll',
  'LHipPitch',
  'LKneePitch',
  'LAnklePitch',
  'LAnkleRoll',
  'RHipYawPitch',
  'RHipRoll',
  'RHipPitch',
  'RKneePitch',
  'RAnklePitch',
  'RAnkleRoll',
  'RShoulderPitch',
  'RShoulderRoll',
  'RElbowYaw',
  'RElbowRoll',
  'RWristYaw',
  'RHand'],
 {'HeadPitch': [-0.78539819, 0.78539819, 0.14381513000000001],
  'HeadYaw': [-1.5707964000000001, 1.5707964000000001, 0.16528267999999999],
  'LAnklePitch': [-1.2217305000000001, 0.78539819, 0.12793263999999999],
  'LAnkleRoll': [-0.78539819, 0.78539819, 0.083077677000000003],
  'LElbowRoll': [-1.6580627999999999, 0.0, 0.14381513000000001],
  'LElbowYaw': [-2.0943952000000001, 2.0943952000000001, 0.16528267999999999],
  'LHand': [0.0, 1.0, 0.14381513000000001],
  'LHipPitch': [-1.5707964000000001,
                0.52359878999999998,
                0.12793263999999999],
  'LHipRoll': [-0.43633232, 0.78539819, 0.083077677000000003],
  'LHipYawPitch': [-0.95993108000000005,
                   0.69813168000000003,
                   0.083077677000000003],
  'LKneePitch': [0.0, 2.2689281000000001, 0.12793263999999999],
  'LShoulderPitch': [-2.0943952000000001,
                     2.0943952000000001,
                     0.16528267999999999],
  'LShoulderRoll': [0.0, 1.6580627999999999, 0.14381513000000001],
  'LWristYaw': [-1.8325956999999999, 2.6179937999999998, 0.14381513000000001],
  'RAnklePitch': [-1.2217305000000001, 0.78539819, 0.12793263999999999],
  'RAnkleRoll': [-0.78539819, 0.78539819, 0.083077677000000003],
  'RElbowRoll': [0.0, 1.6580627999999999, 0.14381513000000001],
  'RElbowYaw': [-2.0943952000000001, 2.0943952000000001, 0.16528267999999999],
  'RHand': [0.0, 1.0, 0.14381513000000001],
  'RHipPitch': [-1.5707964000000001,
                0.52359878999999998,
                0.12793263999999999],
  'RHipRoll': [-0.78539819, 0.43633232, 0.083077677000000003],
  'RHipYawPitch': [-0.95993108000000005,
                   0.69813168000000003,
                   0.083077677000000003],
  'RKneePitch': [0.0, 2.2689281000000001, 0.12793263999999999],
  'RShoulderPitch': [-2.0943952000000001,
                     2.0943952000000001,
                     0.16528267999999999],
  'RShoulderRoll': [-1.6580627999999999, 0.0, 0.14381513000000001],
  'RWristYaw': [-1.8325956999999999, 2.6179937999999998, 0.14381513000000001]})

# Color tables filenames
WEBOTS_TABLE_FILENAME = os.path.join(os.environ['HOME'],
                'src/nao-man/tables/maverick/webots.mtb')

DEFAULT_TABLE_FILENAME = os.path.join(os.environ['HOME'],
                'src/nao-man/tables/maverick/default.mtb')

# Debugging constants
CONSOLE_LINE_LENGTH = 73

# General unknown:
UNKNOWN = object() # Ensures uniqueness, and won't test as equal to anything other than itself.

