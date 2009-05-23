"""
if on a 32 bit code base:
    finds naoqi, fixes sys.path and then imports it.
else:
    currently does nothing
"""

# Test where we are - could be one of simulator, on robot, or remote.
# there is no actual difference between simulator and remote, or actually
# robot - as long as we use the AL_DIR variable. If it doesn't exist, try
# looking in a few default places (but we really should be setting AL_DIR
# all arround - so this is probably a good occasion to use syslog to scream
# at our users).

from . import debug

from burst_util import is64

predefined_sys_paths = [
 # opennao (as came with the robots)
('/opt/naoqi/extern/python/aldebaran',
 '/opt/naoqi/extern/python/aldebaran/geode'
 ),
]

import os
import sys

def fix_sys_path():
    naoqi_root = None
    al_dir = os.environ.get('AL_DIR', None)
    if al_dir != None:
        if not os.path.exists(al_dir):
            print "AL_DIR set to nonexistant path!\nAL_DIR = %s\nQuitting." % al_dir
            raise SystemExit
        base = os.path.join(al_dir, 'extern', 'python')
        dirpath, dirnames, filenames = os.walk(base).next()
        for dirpath in dirnames:
            if os.path.split(dirpath)[-1] != 'proxies':
                second = os.path.join(base, dirpath)
                break
        predefined_sys_paths.insert(0, (base, os.path.join(base, 'aldebaran'), second))
    for paths in predefined_sys_paths:
        if all([os.path.exists(path) for path in paths]):
            sys.path.extend(paths)
            naoqi_root = paths[0]
            naoqi_imp = paths[1]
            break
    if naoqi_root is None:
        print """ERROR: naoqi is not installed. Please install it and make sure the AL_DIR environment
variable points to it. See https://shwarma.cs.biu.ac.il/moin/NaoQi for OS specific instructions
"""
        #raise SystemExit
        print "ERROR: Ignored"

# Set path only after reading command line arguments - we need them to know
# if we are connecting to a simulator.

def find_naoqi():
    try:
        from aldebaran import naoqi
    except:
        try:
            import naoqi
        except:
            pass

    if 'naoqi' not in sys.modules and 'aldebaran' not in sys.modules:
        fix_sys_path()

    print_warning = False
    try:
        from aldebaran import naoqi
    except:
        try:
            import naoqi
        except Exception, e:
            print "naoqi import caused exception (after path fix):", e
            print_warning = True
        except:
            print_warning = True

    if print_warning:
        print "burst did it's best to find naoqi - you are probably either"
        print "forgetting to setup AL_DIR or on a 64 bit machine. Either way"
        print "burst will let you continue, but expect everything to explode."


# maybe this is already taken care of? test first.
if is64():
    print "burst.base - 64 bit architecture, not looking for naoqi"
else:
    find_naoqi()


