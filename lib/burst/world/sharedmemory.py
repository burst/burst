import os
import stat
import struct
import linecache
import mmap

from twisted.python import log

import burst
from burst_util import Deferred, chainDeferreds
from burst_consts import (BURST_SHARED_MEMORY_PROXY_NAME,
    MMAP_FILENAME, MMAP_LENGTH, BURST_SHARED_MEMORY_VARIABLES_START_OFFSET,
    US_DISTANCES_VARNAME, US_ELEMENTS_NUM)

class SharedMemoryReader(object):
    """ read from memory mapped file and not from ALMemory proxy, which
    is painfully slow (but only if the file is there - for example, we
    don't want to break running controllers not on the robot)
    """

    verbose = False

    def __init__(self, varlist):
        """ construct a SharedMemoryReader, given a variable list (names
        from ALMemory). Since this is done in async style, there is a deferred
        for completion of the init called self.openDeferred which
        can be used, i.e. self.openDeferred.addCallback(on_shm_inited)
        """
        if not self.isMMapAvailable():
            raise Exception("Don't initialize me if there is no MMAP!")
        self._shm_proxy = shm_proxy = burst.getBurstMemProxy(deferred=True)
        self._var_names = varlist
        self._fd = None
        self._buf = None
        self._unpack = 'f' * len(self._var_names)
        start_offset = BURST_SHARED_MEMORY_VARIABLES_START_OFFSET
        self._unpack_start = start_offset
        self._unpack_end = start_offset + struct.calcsize(self._unpack)
        self._sonar_unpack = 'f'*US_ELEMENTS_NUM
        self._sonar_start = 0
        self._sonar_end = struct.calcsize(self._sonar_unpack) + self._sonar_start
        self.vars = dict((k, 0.0) for k in self._var_names)
        # TODO - ugly (next year)
        self.vars[US_DISTANCES_VARNAME] = [0.0] * US_ELEMENTS_NUM
        print "SharedMemory: asked burstmem to map %s variables" % len(self._var_names)
        # set all the names of the variables we want mapped - we don't block
        # or anything since we expect the first few frames to be eventless,
        # but this is definitely a TODO
        self.openDeferred = Deferred()
        shm_proxy.clearMappedVariables().addCallback(self._complete_init).addErrback(log.err)

    def _complete_init(self, _):
        # TODO - this is slow but only done on init
        map_d = chainDeferreds([lambda result, i=i, varname=varname: self._shm_proxy.addMappedVariable(i, varname)
            for i, varname in enumerate(self._var_names)])
        map_d.addCallback(lambda _: self._shm_proxy.getNumberOfVariables().addCallback(
            self._reportNumberOfVariablesInBurstmem))
        map_d.addCallback(lambda _:
            self._shm_proxy.isMemoryMapRunning().addCallback(self._completeOpen))
        map_d.addErrback(log.err)

    def _reportNumberOfVariablesInBurstmem(self, num):
        print "SharedMemory: burstmem says it has %s variables" % num

    def _completeOpen(self, mmap_running):
        """ callback for shm_proxy.isMemoryMapRunning called by open """
        print "SharedMemory: _completeOpen: memory mapped = %s (if True then previous session didn't close it)" % mmap_running
        def assertMMAPRunning(is_running):
            assert(is_running)
        self._shm_proxy.startMemoryMap().addCallback(
            lambda _: self._shm_proxy.isMemoryMapRunning().addCallback(assertMMAPRunning)).addErrback(log.err)
        if self._fd is not None: return
        data = open(MMAP_FILENAME, 'r')
        self._fd = fd = data.fileno()
        self._buf = mmap.mmap(fd, MMAP_LENGTH, mmap.MAP_SHARED | mmap.ACCESS_READ, mmap.PROT_READ)
        print "world: shared memory opened successfully"
        self.openDeferred.callback(None)

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
        if not self._buf: return
        values = struct.unpack(self._unpack, self._buf[self._unpack_start:self._unpack_end])
        # TODO - would a single dict.update be faster?
        for k, v in zip(self._var_names, values):
            self.vars[k] = v
        # update sonar variables differently - they are stored at the beginning
        # of the shared memory region
        self.vars[US_DISTANCES_VARNAME] = struct.unpack(self._sonar_unpack,
            self._buf[self._sonar_start:self._sonar_end])
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

