from burst_util import get_hostname

from general_moves import *
from walks import *
from choreograph import *

# Load Robot specific moves (for messi, gerrard, etc.)
try:
    mymoves = __import__('burst.moves.%s' % get_hostname(), fromlist=[''])
    globals().update(mymoves.__dict__)
except:
    pass
