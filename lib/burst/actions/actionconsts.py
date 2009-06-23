"""
Actions constants (as opposed to burst_consts)
"""

import burst.moves.poses as poses
from burst.world import World
from burst_consts import LEFT, RIGHT, DOWN, UP

INITIAL_STIFFNESS  = 1.0 # TODO: Check other stiffnesses, as this might not be optimal.

#25 - TODO - This is "the number of 20ms cycles per step". What should it be?
DEFAULT_STEPS_FOR_TURN = 150
DEFAULT_SLOW_WALK_STEPS = 150 # used only in real-world

MINIMAL_CHANGELOCATION_TURN = 0.15
MINIMAL_CHANGELOCATION_SIDEWAYS = 0.0015
MINIMAL_CHANGELOCATION_X = 0.01

(KICK_TYPE_STRAIGHT, KICK_TYPE_INSIDE) = range(2)

KICK_TYPES = {(KICK_TYPE_STRAIGHT, LEFT): poses.GREAT_KICK_LEFT,
              (KICK_TYPE_STRAIGHT, RIGHT): poses.GREAT_KICK_RIGHT,
              (KICK_TYPE_INSIDE, LEFT): poses.INSIDE_KICK_LEFT,
              (KICK_TYPE_INSIDE, RIGHT): poses.INSIDE_KICK_RIGHT
              }

#(KICK_TYPE_STRAIGHT_WITH_LEFT,
# KICK_TYPE_STRAIGHT_WITH_RIGHT) = range(2)
#
#KICK_TYPES = {KICK_TYPE_STRAIGHT_WITH_LEFT: poses.GREAT_KICK_LEFT,
#              KICK_TYPE_STRAIGHT_WITH_RIGHT: poses.GREAT_KICK_RIGHT}

(LOOKAROUND_QUICK,
 LOOKAROUND_FRONT,
 LOOKAROUND_AROUND) = range(3) # must be zero based - some code depends on it!
LOOKAROUND_TYPES = {LOOKAROUND_QUICK: poses.HEAD_SCAN_QUICK,
                    LOOKAROUND_FRONT: poses.HEAD_SCAN_FRONT,
                    LOOKAROUND_AROUND: poses.HEAD_SCAN_FRONT} # TODO: Add look around
LOOKAROUND_MAX = max(LOOKAROUND_TYPES.keys())
