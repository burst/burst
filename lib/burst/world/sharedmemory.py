import os
import stat
import struct
import linecache
import mmap

import burst
from burst_util import Deferred, chainDeferreds
from burst_consts import (BURST_SHARED_MEMORY_PROXY_NAME,
    MMAP_FILENAME, MMAP_LENGTH, BURST_SHARED_MEMORY_VARIABLES_START_OFFSET)

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
        # set all the names of the variables we want mapped - we don't block
        # or anything since we expect the first few frames to be eventless,
        # but this is definitely a TODO
        self.openDeferred = Deferred()
        self._init_completed = False
        shm_proxy.clearMappedVariables().addCallback(self._complete_init)

    def _complete_init(self, _):
        map_d = chainDeferreds([lambda result, i=i, varname=varname: self._shm_proxy.addMappedVariable(i, varname)
            for i, varname in enumerate(self._var_names)])
        print "SharedMemory: asked burstmem to map %s variables" % len(self._var_names)
        map_d.addCallback(lambda _: self._shm_proxy.getNumberOfVariables().addCallback(
            self.reportNumberOfVariablesInBurstmem))
        self.vars = dict((k, 0.0) for k in self._var_names)
        # TODO - this is slow (but still should be fast compared to ALMemory)
        self._unpack = 'f' * len(self._var_names)
        start_offset = BURST_SHARED_MEMORY_VARIABLES_START_OFFSET
        self._unpack_start = start_offset
        self._unpack_end = start_offset + struct.calcsize(self._unpack)
        self._fd = None
        self._buf = None
        self._init_completed = True
        map_d.addCallback(self._open)

    def reportNumberOfVariablesInBurstmem(self, num):
        print "SharedMemory: burstmem says it has %s variables" % num

    def _open(self, _=None):
        """ start the shared memory proxy to write, and mmap to read """
        if not self._init_completed: return
        self._shm_proxy.isMemoryMapRunning().addCallback(self._completeOpen)
        self.openDeferred.callback(None)

    def _completeOpen(self, mmap_running):
        """ callback for shm_proxy.isMemoryMapRunning called by open """
        if mmap_running: return
        self._shm_proxy.startMemoryMap().addCallback(
            lambda: self._shm_proxy.isMemoryMapRunning().addCallback(assertMMAPRunning))
        def assertMMAPRunning(is_running):
            assert(is_running)
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
        if not self._init_completed: return
        values = struct.unpack(self._unpack, self._buf[self._unpack_start:self._unpack_end])
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

