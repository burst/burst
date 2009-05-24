import burst

from general_moves import *
from walks import *
from choreograph import *

# Load Robot specific moves (for messi, gerrard, etc.)
try:
    mymoves = __import__('burst.moves.%s' % burst.robotname, fromlist=[''])
    globals().update(mymoves.__dict__)
except:
    pass

