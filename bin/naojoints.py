#!/usr/bin/python

# add path to burst lib
import os
import sys

burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)
from burst_consts import ROBOT_IP_TO_NAME

def main():
    import pynaoqi.gui
    pynaoqi.gui.main()

if __name__ == '__main__':
    # check the actual name of the executable - use it as "--ip bla" if it
    # exists in burst_consts.ROBOT_IP_TO_NAME.values()
    exec_name = os.path.split(sys.argv[0])[-1]
    print "CALLED WITH exec_name = %s" % exec_name
    if exec_name in ROBOT_IP_TO_NAME.values() and not '--ip' in sys.argv:
        sys.argv.extend(['--ip', exec_name])
    main()

