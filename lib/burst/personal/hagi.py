""" Personal file for a robot by the name of this file.

PLEASE PAY ATTENTION TO THE FOLLOWING:

There is the good way to update stuff, and the bad way (asaf, I'm looking at you).

# BAD
import moves.walks as walks
walks.SIT_POS = [2,3,4]

# GOOD
import moves.walks as walks
del walks.SIT_POS[:]
walks.SIT_POS.extend([3,4,5])

# ALSO GOOD
walks.SIT_POS[2] = 10

"""

from burst.moves.walks import SLOW_WALK

