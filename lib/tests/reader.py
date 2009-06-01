#!/usr/bin/python

import os
import mmap
import struct

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
    # TODO - this code only works when not getting deferreds.
    num_vars = shm.getNumberOfVariables()
    return [shm.getVarNameByIndex(i) for i in xrange(num_vars)]

def main():
    #fd = os.open(filename, os.O_RDONLY)
    data = open(filename, 'r')
    fd = data.fileno()
    buf = mmap.mmap(fd, totalsize, mmap.MAP_SHARED | mmap.ACCESS_READ, mmap.PROT_READ)

    import sys
    vars = None
    if len(sys.argv) > 1:
        vars = sys.argv[1:]
        total_vars = get_var_names()
        indices = [vars.index(var) for var in total_vars]
        print "indices = %s" % str(indices)
    while True:
        if vars:
            values = [struct.unpack('f', buf[i*4:i*4+4])[0] for i in indices]
            print ' '.join('%10s' % ('%3.3f' % v) for v in values)
        else:
            thesum = sum(struct.unpack('i', buf[i:i+4])[0] for i in xrange(0, totalsize, 4))
            print thesum

if __name__ == '__main__':
    main()

