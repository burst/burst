"""
Field constants.

Parts are shamelessly translated from FieldLines.cpp and
other files in nao-man repository:

http://github.com/northern-bites
"""

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
FIELD_WIDTH = FIELD_GREEN_WIDTH
FIELD_HEIGHT = FIELD_GREEN_HEIGHT

CENTER_FIELD_X = FIELD_GREEN_WIDTH * .5
CENTER_FIELD_Y = FIELD_GREEN_HEIGHT * .5

FIELD_GREEN_LEFT_SIDELINE_X = 0
FIELD_GREEN_RIGHT_SIDELINE_X = FIELD_GREEN_WIDTH
FIELD_GREEN_BOTTOM_SIDELINE_Y = 0
FIELD_GREEN_TOP_SIDELINE_Y = FIELD_GREEN_HEIGHT

FIELD_WHITE_BOTTOM_SIDELINE_Y = GREEN_PAD_Y
FIELD_WHITE_TOP_SIDELINE_Y = (FIELD_WHITE_HEIGHT + GREEN_PAD_Y)

FIELD_WHITE_LEFT_SIDELINE_X = GREEN_PAD_X
FIELD_WHITE_RIGHT_SIDELINE_X = (FIELD_WHITE_WIDTH + GREEN_PAD_X)

MIDFIELD_X = FIELD_GREEN_WIDTH * .5
MIDFIELD_Y = FIELD_GREEN_HEIGHT * .5

# GOAL CONSTANTS
LANDMARK_BLUE_GOAL_BOTTOM_POST_X = FIELD_WHITE_LEFT_SIDELINE_X + GOAL_POST_RADIUS
LANDMARK_BLUE_GOAL_TOP_POST_X = FIELD_WHITE_LEFT_SIDELINE_X + GOAL_POST_RADIUS
LANDMARK_YELLOW_GOAL_BOTTOM_POST_X = FIELD_WHITE_RIGHT_SIDELINE_X - GOAL_POST_RADIUS
LANDMARK_YELLOW_GOAL_TOP_POST_X = FIELD_WHITE_RIGHT_SIDELINE_X - GOAL_POST_RADIUS

LANDMARK_BLUE_GOAL_BOTTOM_POST_Y = CENTER_FIELD_Y - CROSSBAR_CM_WIDTH / 2.0
LANDMARK_BLUE_GOAL_TOP_POST_Y = CENTER_FIELD_Y + CROSSBAR_CM_WIDTH / 2.0
LANDMARK_YELLOW_GOAL_BOTTOM_POST_Y = CENTER_FIELD_Y - CROSSBAR_CM_WIDTH / 2.0
LANDMARK_YELLOW_GOAL_TOP_POST_Y = CENTER_FIELD_Y + CROSSBAR_CM_WIDTH / 2.0

CENTER_CIRCLE_RADIUS = 62.5 # Not scaled

landmarks = [
    (LANDMARK_BLUE_GOAL_BOTTOM_POST_X,
     LANDMARK_BLUE_GOAL_BOTTOM_POST_Y,
     GOAL_POST_RADIUS,
     'blue'),
    (LANDMARK_BLUE_GOAL_TOP_POST_X,
     LANDMARK_BLUE_GOAL_TOP_POST_Y,
     GOAL_POST_RADIUS,
     'blue'),
    (LANDMARK_YELLOW_GOAL_BOTTOM_POST_X,
     LANDMARK_YELLOW_GOAL_BOTTOM_POST_Y,
     GOAL_POST_RADIUS,
     'yellow'),
    (LANDMARK_YELLOW_GOAL_TOP_POST_X,
     LANDMARK_YELLOW_GOAL_TOP_POST_Y,
     GOAL_POST_RADIUS,
     'yellow'),
    (MIDFIELD_X,
     MIDFIELD_Y,
     2.0,
     'red'),
     ]

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
