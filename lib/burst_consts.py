"""
This file must include any constant that is not personal to any robot, and
doesn't change during the life of the program. (i.e., constant).

For instance, don't put any moves in here, or any parameters that are personal.
"""

import os # for HOME

import math
import random # for INITIAL_POSITION of SecondaryKicker on KickOff
from math import tan

from burst.field import * # field constants

# Some stuff that is required first
MESSI = 'messi'
GERRARD = 'gerrard'
CECH = 'cech'
RAUL = 'raul'
MALDINI = 'maldini'
HAGI = 'hagi'
#
WEBOTS = 'webots'

# constants to allow easy switching of naoqi versions (minor api changes)
NAOQI_1_3_8 = 'NaoQi 1.3.8'
NAOQI_1_2_0 = 'NaoQi 1.2.0'

################################################################################
#                                                                              #
#       >>>>         Must-Configure-Correctly Constants       <<<<<<<          #
#                                                                              #
################################################################################

# which version of naoqi are we using
NAOQI_VERSION=NAOQI_1_2_0 # NAOQI_1_3_8

# Wait for a configure event when no game controller present
ALWAYS_CONFIGURE = False # IMPORTANT!! Set to True for the games.

# From teams.cfg, in GameStateVisualizer 2009
BURST_TEAM_NUMBER = 4

# Operating Environment constants
ROBOT_IP_TO_NAME = {
    '192.168.5.126'	: MESSI,
    '192.168.5.170'	: GERRARD,
    '192.168.5.226'	: CECH,
    '192.168.5.168'	: HAGI,
    '192.168.5.224'	: RAUL,
    '192.168.5.228'	: MALDINI,
}
import linecache
hosts = linecache.getlines('/etc/hosts')
__rev = dict([(h,i) for i,h in ROBOT_IP_TO_NAME.items()])
for l in hosts:
    parts = l.split()
    if len(parts) != 2: continue
    ip, host = parts
    if host in ROBOT_IP_TO_NAME.values() and __rev[host] != ip:
        print "WARNING: overriding %s from hosts file, from %s to %s" % (host, __rev[host], ip)
        ROBOT_IP_TO_NAME[ip] = host
# Jersey numbers:
# 1 == goalie
GOALIE_JERSEY = 1
KICKER_JERSEY = 2
SECONDARY_JERSEY = 3

ROBOT_NAME_TO_JERSEY_NUMBER = {
    MESSI: GOALIE_JERSEY,
    CECH: GOALIE_JERSEY,
    HAGI: KICKER_JERSEY,
    RAUL: KICKER_JERSEY,
    MALDINI: SECONDARY_JERSEY,
    GERRARD: SECONDARY_JERSEY,
    WEBOTS: GOALIE_JERSEY, # TODO - overriding command line for robot number, required for webots.
}

# This is what the player script uses, that is to say what the default Player
# uses. The key is the jersey number (1,2,3), the value is the import as in
# toplevel_mod.lower_level_mod.class_name (last part is not the module,
# but a symbol in lower_level_mod)
JERSEY_NUMBER_TO_INITIAL_BEHAVIOR_MODULE_CLASS = {
    GOALIE_JERSEY: 'players.goalie.Goalie',
    KICKER_JERSEY: 'players.kicker.Kicker',
    SECONDARY_JERSEY: 'players.kicker.Kicker',
}

################################################################################
# File locations, Shared memory
################################################################################

# Color tables filenames
WEBOTS_TABLE_FILENAME = os.path.join(os.environ['HOME'],
                'src/burst/data/tables/maverick/webots.mtb')

DEFAULT_TABLE_FILENAME = os.path.join(os.environ['HOME'],
                'src/burst/data/tables/maverick/default.mtb')

# Shared memory constants

# burstmem starts by writing variables for the sonars
BURST_SHARED_MEMORY_VARIABLES_START_OFFSET = 8
MMAP_FILENAME           = "/home/root/burst/lib/etc/burstmem.mmap"
MMAP_LENGTH      = 4096


################################################################################
# Important other constants (parameters for various behaviors)
################################################################################

# shortcut variable, True if this is naoqi version 1.2.0
is_120 = NAOQI_VERSION == NAOQI_1_2_0

# WeAreKickOffTeam (True/False) -> Jersey number -> Ready params (dict)
# 'initial_position' - world coordinates
INITIAL_POSITION = 'initial_position'

SECONDARY_ATTACK_LEFT_INITIAL_Y  = -CENTER_CIRCLE_RADIUS*1.5
SECONDARY_ATTACK_RIGHT_INITIAL_Y =  CENTER_CIRCLE_RADIUS*1.5
SECONDARY_ATTACK_INITIAL_Y = random.choice((SECONDARY_ATTACK_LEFT_INITIAL_Y, SECONDARY_ATTACK_RIGHT_INITIAL_Y))
print "Secondary attacker INITIAL POSITION is %s" % ('LEFT' if
    SECONDARY_ATTACK_INITIAL_Y == SECONDARY_ATTACK_LEFT_INITIAL_Y else 'RIGHT')

GOALIE_DONT_HIDE_DIST = 40.0

# TODO - video white line detection, remove those buffers (turn them into a behavior 'get as close as you can')
WHITE_LINE_BUFFER = 20.0 # cm from white line we compensate for inaccuracy in localization and no white line detection
PENALTEY_BUFFER = 20.0

READY_INITIAL_LOCATIONS = {
    # We are the Kick off team - Attacking positions
    True: {
        GOALIE_JERSEY: {
            INITIAL_POSITION: (0.0, 0.0), # TODO - lambda that determines? would be pretty cool
        },
        KICKER_JERSEY: {
            INITIAL_POSITION: (MIDFIELD_X - WHITE_LINE_BUFFER, 0.0),
        },
        SECONDARY_JERSEY: {
            INITIAL_POSITION: (MIDFIELD_X - WHITE_LINE_BUFFER, SECONDARY_ATTACK_INITIAL_Y),
        },
    },
    False: {
        GOALIE_JERSEY: {
            INITIAL_POSITION: (0.0, 0.0),
        },
        KICKER_JERSEY: {
            INITIAL_POSITION: (OUR_PENALTEY_X - PENALTEY_BUFFER, OUR_PENALTEY_Y - GOALIE_DONT_HIDE_DIST),
        },
        SECONDARY_JERSEY: {
            INITIAL_POSITION: (OUR_PENALTEY_X - PENALTEY_BUFFER, OUR_PENALTEY_Y + GOALIE_DONT_HIDE_DIST),
        },
    }
}

# Event Manager constants
DEFAULT_EVENT_MANAGER_DT = 0.1 # seconds. Main loop - we have a polling loop (ayeee). changaeble from --dt

MISSING_FRAMES_MINIMUM = 10

MIN_BEARING_CHANGE = 1e-3 # TODO - ?
MIN_DIST_CHANGE = 1e-3

# Robot constants

# Acceptable Centering error - normalized values (in [-1, 1])
DEFAULT_NORMALIZED_CENTERING_X_ERROR = 0.05*4 #0.05*3
DEFAULT_NORMALIZED_CENTERING_Y_ERROR = 0.05*4 #0.05*3
CENTERING_MINIMUM_PITCH = -0.5 #-0.637

# Sensor constants
# Threshold for differing between leg with/without weight (x>0.00225 means leg DOES carry weight)
# This value is the SUM of the 4 leg sensors (we use 1/x, where x is 1 FSR sensor reading)
FSR_LEG_PRESSED_THRESHOLD = 0.00225
INERTIAL_HISTORY = 10
FSR_HISTORY = 10

################################################################################
################################################################################
SONAR_PRECISION = 0.1 # only required for newer Naoqi, 1.3.8

if NAOQI_VERSION == NAOQI_1_3_8:
    VIDEO_MODULE = 'ALVideoDevice'
    US_DISTANCES_VARNAME = "extractors/alsonar/distances"
    SONAR_MODULE = 'ALSonar'
    VIDEO_MODULE_SUBSCRIBE = 'subscribe'
    VIDEO_MODULE_UNSUBSCRIBE = 'unsubscribe'
    SONAR_EXTRACTOR_SUBSCRIBE = lambda module, myname, dt_ms: module.subscribe(myname, dt_ms, SONAR_PRECISION)
else: # using NAOQI_1_2_0
    VIDEO_MODULE = 'NaoCam'
    US_DISTANCES_VARNAME = "extractors/alultrasound/distances"
    SONAR_MODULE = 'ALUltraSound'
    VIDEO_MODULE_SUBSCRIBE = 'register'
    VIDEO_MODULE_UNSUBSCRIBE = 'unregister'
    SONAR_EXTRACTOR_SUBSCRIBE = lambda module, myname, dt_ms: module.subscribe(myname, [dt_ms])

MIN_JERSEY_NUMBER, MAX_JERSEY_NUMBER = 1, 3
GAME_CONTROLLER_BROADCAST_PORT = 3838
GAME_CONTROLLER_NUM_PLAYERS = 11
GAME_CONTROLLER_NUM_TEAMS = 2

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

# Unit constants
M_TO_CM  = 100.0
CM_TO_M  = 0.01
CM_TO_MM = 10.0
MM_TO_CM = 0.1

# Math constants
INFTY = 1E+37

DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi
CM_TO_METER = 100. # yeah, seems stupid, but probably better than using 100 throughout the code...

# Coordinate system

X_AXIS, Y_AXIS, Z_AXIS, W_AXIS = 0, 1, 2, 3
X, Y, Z = 0, 1, 2

# Camera / Vision constants

# Nao-Man ID Certainty Enumeration
ID_NOT_SURE, ID_MILDLY_SURE, ID_SURE = 0, 1, 2

# setting top/bottom camera
CAMERA_WHICH_PARAM = 18
CAMERA_WHICH_BOTTOM_CAMERA = 1
CAMERA_WHICH_TOP_CAMERA = 0
# NOTE: these are identicle to the ones in ALImageTranscriber::TOP_CAMERA/BOTTOM_CAMERA,
#       and care should be taken to keep it that way.

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

# World constants

BALL_REAL_DIAMETER = 8.7 # cm
ROBOT_DIAMETER = 58.0    # this is from Appendix A of Getting Started - also, doesn't hands raised into account
GOAL_POST_HEIGHT = 80.0
GOAL_POST_DIAMETER = 80.0 # TODO: name? this isn't the radius*2 of the base, it is the diameter in the sense of longest line across an image of the post.

LEFT = 0
RIGHT = 1
DOWN = 2
UP = 3

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

# Sonar constants
US_ELEMENTS_NUM = 2
US_HISTORY_SIZE = 4 # size of history buffer (500ms * 4 frames = ~1 second)
US_NEAR_DISTANCE = 0.4 # distance in meters
US_FRAMES_TILL_LOST = 3 # 3 frames * 500ms = ~1.5 before declaring object as lost

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

# Debugging constants
CONSOLE_LINE_LENGTH = 73

# General unknown:
UNKNOWN = object() # Ensures uniqueness, and won't test as equal to anything other than itself.

# Colors for the LEDs
RED = 0xFF0000; GREEN = 0x00FF00; BLUE = 0x0000FF; OFF = 0x000000; YELLOW = 0xFFFF00; PURPLE = 0xFF00FF; WHITE = 0xFFFFFF; LIGHT_BLUE = 0x00FFFF
TeamColors = {0: BLUE, 1: RED}

# add all the gamecontroller constants (happens at the end since
# gamecontroller_consts uses some consts from here, for led colors)
from gamecontroller_consts import *

