"""
Actions constants (as opposed to burst.consts)
"""

import burst.moves as moves
from burst.world import World
from burst.consts import LEFT, RIGHT, DOWN, UP

INITIAL_STIFFNESS  = 0.85 # TODO: Check other stiffnesses, as this might not be optimal.

#25 - TODO - This is "the number of 20ms cycles per step". What should it be?
if World.connected_to_nao:
    DEFAULT_STEPS_FOR_TURN = 150
    DEFAULT_STEPS_FOR_WALK = 150 # used only in real-world
    DEFAULT_STEPS_FOR_SIDEWAYS = 60
else:
    DEFAULT_STEPS_FOR_TURN = 60
    DEFAULT_STEPS_FOR_WALK = 60
    DEFAULT_STEPS_FOR_SIDEWAYS = 60

MINIMAL_CHANGELOCATION_TURN = 0.15
MINIMAL_CHANGELOCATION_SIDEWAYS = 0.005
MINIMAL_CHANGELOCATION_X = 0.01

(KICK_TYPE_STRAIGHT,
 KICK_TYPE_PASSING) = range(2)

KICK_TYPES = {(KICK_TYPE_STRAIGHT, LEFT): moves.GREAT_KICK_LEFT,
              (KICK_TYPE_STRAIGHT, RIGHT): moves.GREAT_KICK_RIGHT,
              (KICK_TYPE_PASSING, LEFT): moves.GREAT_KICK_LEFT,
              (KICK_TYPE_PASSING, RIGHT): moves.GREAT_KICK_RIGHT}

#(KICK_TYPE_STRAIGHT_WITH_LEFT,
# KICK_TYPE_STRAIGHT_WITH_RIGHT) = range(2)
# 
#KICK_TYPES = {KICK_TYPE_STRAIGHT_WITH_LEFT: moves.GREAT_KICK_LEFT,
#              KICK_TYPE_STRAIGHT_WITH_RIGHT: moves.GREAT_KICK_RIGHT}

(LOOKAROUND_QUICK,
 LOOKAROUND_FRONT,
 LOOKAROUND_AROUND) = range(3)
LOOKAROUND_TYPES = {LOOKAROUND_QUICK: moves.HEAD_SCAN_QUICK,
                    LOOKAROUND_FRONT: moves.HEAD_SCAN_FRONT,
                    LOOKAROUND_AROUND: moves.HEAD_SCAN_FRONT} # TODO: Add look around
