#!/usr/bin/python

"""
Test the memory mapped file used in liue of ALProxy("ALMemory").

to use:
first run any of the players, i.e. players/donothing.py
then run this with two vars, the first index to display and the last.
i.e., for ball:
./reader.py 26 84
"""

import os
import mmap
import struct
import time
import sys
sys.path.append('..')
import burst
from burst.consts import MMAP_LENGTH as totalsize
from burst.consts import MMAP_FILENAME as filename
from burst.consts import BURST_SHARED_MEMORY_PROXY_NAME

if not os.path.exists(filename):
    print "run feeder first to create %s" % filename
    raise SystemExit

MAX_INT = 1<<32

def get_var_names():
    shm = burst.ALProxy(BURST_SHARED_MEMORY_PROXY_NAME)
    shm = get_burst()
    # TODO - this code only works when not getting deferreds.
    num_vars = shm.getNumberOfVariables()
    return [shm.getVarNameByIndex(i) for i in xrange(num_vars)]

def display_vars(indices):
    data = open(filename, 'r')
    fd = data.fileno()
    buf = mmap.mmap(fd, totalsize, mmap.MAP_SHARED | mmap.ACCESS_READ, mmap.PROT_READ)
    while True:
        vars = [struct.unpack('f', buf[i*4:i*4+4])[0] for i in indices]
        print vars
        time.sleep(0.5)

def main():
    #fd = os.open(filename, os.O_RDONLY)

    import sys
    vars = None
    display_vars(range(int(sys.argv[1]), int(sys.argv[2])))
    return
    if len(sys.argv) > 1:
        vars = sys.argv[1:]
        total_vars = get_var_names()
        indices = [vars.index(var) for var in total_vars]
        print "indices = %s" % str(indices)

if __name__ == '__main__':
    main()
