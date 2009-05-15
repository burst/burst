"""
Boot strapping help for the players - add location of burst library
to the path.
"""

import os
in_tree_dir = os.path.realpath(os.path.join(os.environ['HOME'], 'src/burst/lib/players'))
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

