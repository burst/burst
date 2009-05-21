#!/usr/bin/python

# add path to burst lib
import os
import sys
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi.gui

if __name__ == '__main__':
    pynaoqi.gui.main()

