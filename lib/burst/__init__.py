"""
Main entry point for naoqi usage in burst code.

Usage:

import burst
burst.init() # creates connection to broker
motion_proxy = burst.getMotionProxy()
# ... do stuff with motion_proxy

"""

import sys

# Global debug flag. Not actually used in burst, but expected to be checked
# by user code.
debug = False # set to False when checking in

def default_help():
    return "usage: %s [--port=<port>] [--ip=<ip>]" % sys.argv[0]

def test():
    print "naoqi = %s" % naoqi
    print "ip    = %s" % ip
    print "port  = %s" % port
    print
    if '--bodyposition' in sys.argv:
        import bodyposition
        bodyposition.read_until_ctrl_c()
    else:
        print "you can use various switches to test the nao:"
        print default_help() + ' [--bodyposition]'
        print "--bodyposition - enter an endless loop printing various sensors (good for testing)"

# We will daemonize at this point? before anything else:
if '--daemonize' in sys.argv:
    import daemon
    retcode = daemon.createDaemon()

# must be the first import - you can only import naoqi after this
from base import *
from options import *
import burst_target as target

# Finally we load the networking/ipc library to connect to naoqi which does
# actually talk to the hardware. We have two implementations and two development
# hosts, namely 64 bit and 32bit, so this gets a little complex.

from burst_util import is64
import sys

using_pynaoqi = False

if 'pynaoqi' in sys.modules or is64() or options.use_pynaoqi:
    if is64():
        print "64 bit architecture - LESS TESTED"
    else:
        print "32 bit + pynaoqi - LESS TESTED"
    from naoqi_pynaoqi import *
    using_pynaoqi = True

    def init(*args, **kw):
        pass

else:
    # put all of naoqi namespace in burst (wrapped in try to work under pynaoqi
    # import burst.moves as moves)
    try:
        from naoqi import *
    # Note: Bare exception since Exception doesn't catch "wrong ELF class: ELFCLASS32" exceptions
    except:
        pass

    # import any submodules of burst (must happen last!)
    from naoqi_extended import *

    def init(**kw):
        naoqi_extended.init(**kw)

# Personalization happens here, after all of the burst namespace is
# setup, but before burst has finished __init__.py, so user couldn't
# have used it yet.
#
# That means anyone who imports burst gets a personalized version.

print "Loading Personalization for %s.." % target.robotname,
personal_filename = 'burst.personal.%s' % target.robotname

if options.debug_personal:
    __import__(personal_filename) # any error will be thrown to the interpreter
try:
    __import__(personal_filename)
except ImportError, e:
    print "\nERROR: Personalization missing: %s" % e
    print "       using no personalization"
except Exception, e:
    # TODO - this swallowes the actual error - the traceback is useless, at
    # least for syntax errors.
    print "\nERROR: Exception while importing %s: %s" % (personal_filename, e)
    import traceback
    import sys
    traceback.print_exc()
    raise SystemExit

print "Done"



if __name__ == '__main__':
    test()

