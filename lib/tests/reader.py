#!/usr/bin/python

import os
import mmap
import struct

import sys
sys.path.append('..')
import burst
from burst.consts import MMAP_LENGTH as totalsize
from burst.consts import MMAP_FILENAME as filename

if not os.path.exists(filename):
    print "run feeder first to create %s" % filename
    raise SystemExit

MAX_INT = 1<<32

def main():
    #fd = os.open(filename, os.O_RDONLY)
    data = open(filename, 'r')
    fd = data.fileno()
    buf = mmap.mmap(fd, totalsize, mmap.MAP_SHARED | mmap.ACCESS_READ, mmap.PROT_READ)
    while True:
        thesum = sum(struct.unpack('i', buf[i:i+4])[0] for i in xrange(0, totalsize, 4))
        print thesum

if __name__ == '__main__':
    main()

