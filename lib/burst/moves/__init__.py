import burst

# array with names of attributes of this module that can be run with executeMove
# in the naojoints utility (burst/bin/naojoints.py)
NAOJOINTS_EXECUTE_MOVE_MOVES = "INITIAL_POS SIT_POS ZERO_POS STAND STAND_UP_FRONT STAND_UP_BACK GREAT_KICK_LEFT GREAT_KICK_RIGHT".split()

#from walks import * # users should start using moves.walks instead
# allows for easier personalization.
from choreograph import *


