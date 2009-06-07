#!/usr/bin/python

# add path to burst lib
import os
import sys

burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)
from burst_consts import ROBOT_IP_TO_NAME
from burst_util import set_robot_ip_from_argv

def main():
    import pynaoqi.gui
    pynaoqi.gui.main()

if __name__ == '__main__':
    set_robot_ip_from_argv()
    main()

