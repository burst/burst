import os
import stat
import struct
import linecache
import mmap

import burst
from burst_consts import (BURST_SHARED_MEMORY_PROXY_NAME,
    MMAP_FILENAME, MMAP_LENGTH)

class SharedMemoryReader(object):
    """ read from memory mapped file and not from ALMemory proxy, which
    is painfully slow (but only if the file is there - for example, we
    don't want to break running controllers not on the robot)
    """

    verbose = False

    def __init__(self, varlist):
        if not self.isMMapAvailable():
            raise Exception("Don't initialize me if there is no MMAP!")
        self._shm_proxy = shm_proxy = burst.ALProxy(BURST_SHARED_MEMORY_PROXY_NAME)
        # set all the names of the variables we want mapped - we don't block
        # or anything since we expect the first few frames to be eventless,
        # but this is definitely a TODO
        shm_proxy.clearMappedVariables()
        for i, varname in enumerate(varlist):
            shm_proxy.addMappedVariable(i, varname)
        print "SharedMemory: asked burstmem to map %s variables" % len(varlist)
        d_or_num = shm_proxy.getNumberOfVariables()
        # TODO - ugly, and untested (also - maybeDeferred?)
        if isinstance(d_or_num, int):
            self.reportNumberOfVariablesInBurstmem(d_or_num)
        else:
            d_or_num.addCallback(self.reportNumberOfVariablesInBurstmem)
        self._var_names = varlist
        self.vars = dict((k, 0.0) for k in self._var_names)
        # TODO - this is slow (but still should be fast compared to ALMemory)
        self._unpack = 'f' * len(self._var_names)
        self._unpack_size = struct.calcsize(self._unpack)
        self._fd = None
        self._buf = None

    def reportNumberOfVariablesInBurstmem(self, num):
        print "SharedMemory: burstmem says it has %s variables" % num

    def open(self):
        """ start the shared memory proxy to write, and mmap to read """
        if not self._shm_proxy.isMemoryMapRunning(): # blocking
            self._shm_proxy.startMemoryMap()
            assert(self._shm_proxy.isMemoryMapRunning())
        if self._fd is not None: return
        data = open(MMAP_FILENAME, 'r')
        self._fd = fd = data.fileno()
        self._buf = mmap.mmap(fd, MMAP_LENGTH, mmap.MAP_SHARED | mmap.ACCESS_READ, mmap.PROT_READ)
        print "world: shared memory opened successfully"
    
    def close(self):
        if self._fd is None: return
        # no mmap.munmap??
        self._fd.close()
        self._fd = None
        self._buf = None

    def update(self):
        # TODO - this is slow
        # TODO - instead of updating the dict I could just update the
        # values and only make the dict if someone explicitly wants it,
        # and give values using cached indices created in constructor.
        values = struct.unpack(self._unpack, self._buf[:self._unpack_size])
        # TODO - would a single dict.update be faster?
        for k, v in zip(self._var_names, values):
            self.vars[k] = v
        if self.verbose:
            print self.vars

    @classmethod
    def isMMapAvailable(cls):
        return (os.path.exists(MMAP_FILENAME))

    @classmethod
    def tryToInitMMap(cls):
        """ This is just the mmap setup file hidden in a class variable here.
        It is perfectly safe to run on a regular computer since it won't
        do anything if it finds it isn't on a nao, and only creates a file
        if there is none there right now.
        """
        if not os.path.exists(MMAP_FILENAME):
            fd = open(MMAP_FILENAME, "w+")
            fd.write(MMAP_LENGTH*"\00")
            fd.close()
            assert(os.path.exists(MMAP_FILENAME))
            assert(os.stat(MMAP_FILENAME)[stat.ST_SIZE] == MMAP_LENGTH)

