import math

# Proxy names
BURST_SHARED_MEMORY_PROXY_NAME = "burstmem"
BURST_RECORDER_PROXY_NAME = "recorder"

# Naoqi Constants

BALANCE_MODE_OFF = 0
BALANCE_MODE_AUTO = 1
BALANCE_MODE_COM_CONTROL = 2

# support modes
SUPPORT_MODE_LEFT, SUPPORT_MODE_DOUBLE_LEFT, SUPPORT_MODE_RIGHT, SUPPORT_MODE_DOUBLE_RIGHT = 0, 1, 2, 3

INTERPOLATION_LINEAR, INTERPOLATION_SMOOTH = 0, 1

# Math constants

DEG_TO_RAD = math.pi / 180.0
CM_TO_METER = 100. # yeah, seems stupid, but probably better than using 100 throughout the code...

# Camera / Vision constants

IMAGE_WIDTH = 320.0
IMAGE_HEIGHT = 240.0

IMAGE_HALF_WIDTH = IMAGE_WIDTH / 2
IMAGE_HALF_HEIGHT = IMAGE_HEIGHT / 2

# Shared memory constants

MMAP_VARIABLES_FILENAME = "/home/root/burst/lib/etc/mmap_variables.txt"
MMAP_FILENAME           = "/home/root/burst/lib/etc/burstmem.mmap"
MMAP_LENGTH      = 4096

# Event Manager constants
EVENT_MANAGER_DT = 0.05

# World constants

MISSING_FRAMES_MINIMUM = 10

MIN_BEARING_CHANGE = 1e-3 # TODO - ?
MIN_DIST_CHANGE = 1e-3

BALL_REAL_DIAMETER = 8.7 # cm
ROBOT_DIAMETER = 58.0    # this is from Appendix A of Getting Started - also, doesn't hands raised into account
GOAL_POST_HEIGHT = 80.0
GOAL_POST_DIAMETER = 80.0 # TODO: name? this isn't the radius*2 of the base, it is the diameter in the sense of longest line across an image of the post.

# Robot constants
MOTION_FINISHED_MIN_DURATION = EVENT_MANAGER_DT * 3


