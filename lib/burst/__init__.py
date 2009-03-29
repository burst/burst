"""
Main entry point for naoqi usage in burst code.

Usage:

import burst
burst.init() # creates connection to broker
motion_proxy = burst.getMotionProxy()
# ... do stuff with motion_proxy

"""

# Global debug flag. Not actually used in burst, but expected to be checked
# by user code.
debug = False # set to False when checking in

def init():
    robot.init()

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

# must be the first import - you can only import naoqi after this
from base import *

# put all of naoqi namespace in burst
from naoqi import *

# import any submodules of burst (must happen last!)
from robot import *

if __name__ == '__main__':
    test()

