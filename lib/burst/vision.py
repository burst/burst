""" Beginning of some vision computations - nothing useful here right now.
"""
from consts import DEG_TO_RAD

#### Vision constants
FOV_X = 46.4 * DEG_TO_RAD
FOV_Y = 34.8 * DEG_TO_RAD
IMAGE_WIDTH  = 0.236 # cm - i.e 2.36 mm
IMAGE_HEIGHT = 0.176 # cm
FOCAL_LENGTH = IMAGE_HEIGHT / 2.0 / atan(FOV_Y / 2)

# TODO - ask the V.I.M.
IMAGE_PIXELS_HEIGHT = 320

DISTANCE_FACTOR = IMAGE_PIXELS_HEIGHT * IMAGE_HEIGHT / FOCAL_LENGTH

# Vision primitives

def getObjectDistanceFromHeight(height_in_pixels, real_height_in_cm):
    """ TODO: This is the actual Height, i.e. z axis. This will work fine
    as long as the camera is actually level, i.e. pitch is zero. But that is not
    the general case - so to fix this, this method needs to take that into account,
    either by getting the pitch or getting a real_heigh_in_cm that is times the sin(pitch)
    or something like that/
    """
    return DISTANCE_FACTOR / height_in_pixels * real_height_in_cm



