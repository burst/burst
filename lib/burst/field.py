"""
Field constants.

Parts are shamelessly translated from FieldConstants.h and
other files in nao-man repository:

http://github.com/northern-bites
"""

# LENGTH constants - don't care what the coordinate system
# is, there are constant.

FIELD_WHITE_WIDTH = 605.0
FIELD_WHITE_HEIGHT = 405.0
GREEN_PAD_X = 67.5
GREEN_PAD_Y = 67.5

GOAL_POST_CM_HEIGHT = 80.0
GOAL_POST_CM_WIDTH = 10.0
CROSSBAR_CM_WIDTH = 140.
CROSSBAR_CM_HEIGHT = 5.0
GOAL_POST_RADIUS = GOAL_POST_CM_WIDTH / 2.0

FIELD_GREEN_WIDTH = FIELD_WHITE_WIDTH + 2.0 * GREEN_PAD_Y
FIELD_GREEN_HEIGHT = FIELD_WHITE_HEIGHT + 2.0 * GREEN_PAD_X
FIELD_WIDTH = FIELD_WHITE_WIDTH   #  XXX: Northern use GREEN
FIELD_HEIGHT = FIELD_WHITE_HEIGHT #        -"-

# LANDMARK CONSTANTS

BURST_WORLD_FRAME_DOC = """
Our world frame is the following, described right after:

               .-----------------------------------------.
               |                                         |
               | ^ - - - - - - - - - - - - - - - - - - ^ |
               |                                         |
               | Y                                     ; |
               | ^                                       |
               | B                                     Y |
               | |                                       |
               | O---->X                                 |
               |                                         |
               | B                                     Y |
               |                                         |
               | ;                                     ; |
               |                                         |
               | V - - - - - - - - - - - - - - - - - - V |
               |                                         |
               .-----------------------------------------.

The "^" and "V" are the corners of the WHITE (inner, playable) field.

The "." are the corners of the GREEN (outer) field.

The O is the origin of the coordinate frame.

Y is either the Yellow goal posts or the Y axis.

X is the X axis.

B is the Blue goal.

"|-;" are line chars for the white borders or for the green 'edge'
"""

# Center of field, where ball is placed on kick-off.
MIDFIELD_X = FIELD_WIDTH * .5
MIDFIELD_Y = 0.0

BLUE_GOAL_BOTTOM_POST_X, BLUE_GOAL_BOTTOM_POST_Y = (
    0.0, -(CROSSBAR_CM_WIDTH/2.0 + GOAL_POST_RADIUS) )
BLUE_GOAL_TOP_POST_X, BLUE_GOAL_TOP_POST_Y = (
    0.0, CROSSBAR_CM_WIDTH/2.0 + GOAL_POST_RADIUS)
YELLOW_GOAL_BOTTOM_POST_X, YELLOW_GOAL_BOTTOM_POST_Y = (
    FIELD_WIDTH, -(CROSSBAR_CM_WIDTH/2.0 + GOAL_POST_RADIUS) )
YELLOW_GOAL_TOP_POST_X, YELLOW_GOAL_TOP_POST_Y = (
    FIELD_WIDTH, CROSSBAR_CM_WIDTH/2.0 + GOAL_POST_RADIUS)

FIELD_GREEN_LEFT_SIDELINE_X = -GREEN_PAD_X
FIELD_GREEN_RIGHT_SIDELINE_X = FIELD_GREEN_WIDTH - GREEN_PAD_X
FIELD_GREEN_BOTTOM_SIDELINE_Y = -FIELD_WHITE_HEIGHT / 2.0 - GREEN_PAD_Y
FIELD_GREEN_TOP_SIDELINE_Y = FIELD_WHITE_HEIGHT / 2.0 + GREEN_PAD_Y

FIELD_WHITE_LEFT_SIDELINE_X = 0.0
FIELD_WHITE_RIGHT_SIDELINE_X = FIELD_WHITE_WIDTH
FIELD_WHITE_BOTTOM_SIDELINE_Y = -FIELD_WHITE_HEIGHT / 2.0
FIELD_WHITE_TOP_SIDELINE_Y = FIELD_WHITE_HEIGHT / 2.0

def NB():
    """ NB use a coordinate system that has the same axes but different
    origin when compares to Burst.
    NB_Origin is at the bottom left corner of the GREEN (outer) field,
    when the blue gate is on the left side and looking from above, so:

      B         Y

      B         Y

     O

    Burst coordinate frame is different, and stated above
    """
    FIELD_GREEN_LEFT_SIDELINE_X = 0
    FIELD_GREEN_RIGHT_SIDELINE_X = FIELD_GREEN_WIDTH
    FIELD_GREEN_BOTTOM_SIDELINE_Y = 0
    FIELD_GREEN_TOP_SIDELINE_Y = FIELD_GREEN_HEIGHT

    FIELD_WHITE_BOTTOM_SIDELINE_Y = GREEN_PAD_Y
    FIELD_WHITE_TOP_SIDELINE_Y = (FIELD_WHITE_HEIGHT + GREEN_PAD_Y)

    FIELD_WHITE_LEFT_SIDELINE_X = GREEN_PAD_X
    FIELD_WHITE_RIGHT_SIDELINE_X = (FIELD_WHITE_WIDTH + GREEN_PAD_X)

    LANDMARK_BLUE_GOAL_BOTTOM_POST_X = (FIELD_WHITE_LEFT_SIDELINE_X +
        GOAL_POST_RADIUS)
    LANDMARK_BLUE_GOAL_TOP_POST_X = (FIELD_WHITE_LEFT_SIDELINE_X +
        GOAL_POST_RADIUS)
    LANDMARK_YELLOW_GOAL_BOTTOM_POST_X = (FIELD_WHITE_RIGHT_SIDELINE_X -
        GOAL_POST_RADIUS)
    LANDMARK_YELLOW_GOAL_TOP_POST_X = (FIELD_WHITE_RIGHT_SIDELINE_X -
        GOAL_POST_RADIUS)

    LANDMARK_BLUE_GOAL_BOTTOM_POST_Y = CENTER_FIELD_Y - CROSSBAR_CM_WIDTH / 2.0
    LANDMARK_BLUE_GOAL_TOP_POST_Y = CENTER_FIELD_Y + CROSSBAR_CM_WIDTH / 2.0
    LANDMARK_YELLOW_GOAL_BOTTOM_POST_Y = CENTER_FIELD_Y - CROSSBAR_CM_WIDTH / 2.0
    LANDMARK_YELLOW_GOAL_TOP_POST_Y = CENTER_FIELD_Y + CROSSBAR_CM_WIDTH / 2.0

    return locals()

CENTER_CIRCLE_RADIUS = 62.5 # Not scaled

class Landmark(object):
    def __init__(self, x, y, radius, color):
        self.xy = (x, y)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
    def __iter__(self):
        """ for debugging, converts to suitable parameters
        to CanvasTicker constructor """
        return iter([self.x, self.y, self.radius, self.color])

class Goal(object):
    def __init__(self, bottom_post, top_post):
        self.top_post = top_post
        self.bottom_post = bottom_post

landmarks = [Landmark(*lm) for lm in
    [(BLUE_GOAL_BOTTOM_POST_X,
     BLUE_GOAL_BOTTOM_POST_Y,
     GOAL_POST_RADIUS,
     'blue'),
    (BLUE_GOAL_TOP_POST_X,
     BLUE_GOAL_TOP_POST_Y,
     GOAL_POST_RADIUS,
     'blue'),
    (YELLOW_GOAL_BOTTOM_POST_X,
     YELLOW_GOAL_BOTTOM_POST_Y,
     GOAL_POST_RADIUS,
     'yellow'),
    (YELLOW_GOAL_TOP_POST_X,
     YELLOW_GOAL_TOP_POST_Y,
     GOAL_POST_RADIUS,
     'yellow'),
    (MIDFIELD_X,
     MIDFIELD_Y,
     2.0,
     'red'),]]

blue_goal = Goal(landmarks[0], landmarks[1])
yellow_goal   = Goal(landmarks[2], landmarks[3])

white_field = (
    ((FIELD_WHITE_LEFT_SIDELINE_X,
      FIELD_WHITE_BOTTOM_SIDELINE_Y),
     FIELD_WHITE_WIDTH,
     FIELD_WHITE_HEIGHT),
     'white',
)

green_field = (
    ((FIELD_GREEN_LEFT_SIDELINE_X,
      FIELD_GREEN_BOTTOM_SIDELINE_Y),
     FIELD_GREEN_WIDTH,
     FIELD_GREEN_HEIGHT),
     'green',
)

rects = (green_field, white_field)

green_limits = (FIELD_GREEN_LEFT_SIDELINE_X,
    FIELD_GREEN_RIGHT_SIDELINE_X,
    FIELD_GREEN_BOTTOM_SIDELINE_Y,
    FIELD_GREEN_TOP_SIDELINE_Y)

white_limits = (FIELD_WHITE_LEFT_SIDELINE_X,
    FIELD_WHITE_RIGHT_SIDELINE_X,
    FIELD_WHITE_BOTTOM_SIDELINE_Y,
    FIELD_WHITE_TOP_SIDELINE_Y)

