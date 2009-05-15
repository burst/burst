"""
Units:
 Angles - radians
 Lengths - cm
"""

from time import time
import os
import stat
import sys
import mmap
import struct
import linecache

import burst
from ..events import *
from ..sensing import FalldownDetector
from burst_util import running_average

from ..consts import *

from .sharedmemory import *
from .objects import Ball, GoalPost
from .robot import Robot
from .team import Team
from .computed import Computed

def timeit(tmpl):
    def wrapper(f):
        def wrap(*args, **kw):
            t = time()
            ret = f(*args, **kw)
            print tmpl % ((time() - t) * 1000)
            return ret
        return wrap
    return wrapper
###############################################################################
###############################################################################

def cross(*args):
    if len(args) == 1:
        for x in args[0]:
            yield tuple([x])
        raise StopIteration
    for x in args[0]:
        for rest in cross(*args[1:]):
            yield tuple([x] + list(rest))

def gethostname():
    fd = open('/etc/hostname')
    hostname = fd.read().strip().lower() # all hostnames should be lower, we just enforce it..
    fd.close()
    return hostname

class World(object):

    # TODO - move this to __init__?
    isRealNao = os.path.exists('/opt/naoqi/bin/naoqi')
    hostname = gethostname()

    def getRecorderVariableNames(self):
        joints = self.jointnames
        chains = self.chainnames

        # Recording of joints / sensors
        dcm_one_time_vars = ['DCM/HeatLogPath', 'DCM/I2Cpath', 'DCM/RealtimePriority']
        self._record_file = self._record_csv = None
        # Center of mass (computed)
        com = ['Motion/Spaces/World/Com/%s/%s' % args for args in cross(
            ['Sensor', 'Command'], 'XYZ')] + ['Motion/BodyCommandAngles']
        # various dcm stuff
        dcm = ['DCM/Realtime', 'DCM/Time', 'DCM/TargetCycleTime',
           'DCM/CycleTime', 'DCM/Simulation', 'DCM/hardnessMode',
           'DCM/CycleTimeWarning']
        # Joint positions
        jsense = ['Device/SubDeviceList/%s/Position/Sensor/Value' % j for j in
            joints]
        # Actuator commanded position
        actsense = ['Device/SubDeviceList/%s/%s/Value' % args for args in cross(
            joints, ['ElectricCurrent/Sensor',
                'Hardness/Actuator', 'Position/Actuator'])]
        # inertial sensors
        inert = ['Device/SubDeviceList/InertialSensor/%s/Sensor/Value' % sense
            for sense in [
                'AccX', 'AccY', 'AccZ', 'AngleX', 'AngleY',
                'GyrRef', 'GyrX', 'GyrY']]
        # Force SensoR
        force = ['Device/SubDeviceList/%s/FSR/%s/Sensor/Value' % args for args in
            cross(['RFoot', 'LFoot'],
            ['FrontLeft', 'FrontRight', 'RearLeft', 'RearRight'])]
        # position of chains and __?
        poschains = ['Motion/Spaces/Body/%s/Sensor/Position/%s' % args
            for args in cross(chains, ['WX', 'WY', 'WZ', 'X', 'Y', 'Z'])]
        transform = ['Motion/Spaces/World/Transform/%s' % coord for coord in
            ['WX', 'WY', 'WZ', 'X', 'Y', 'Z']]
        # Various other stuff
        various = ['Motion/SupportMode', 'Motion/Synchro', 'Motion/Walk/Active',
               'MotorAngles', 'WalkIsActive', 'extractors/alinertial/position']
        return (com + dcm + jsense + actsense + inert + force +
                poschains + transform + various)

    def __init__(self):
        # TODO - try to get the "/BURST/*" variables from ALMemory and complain if they
        # are not there (same as the old "can't find MAN module", only now there isn't one)
        self._memory = burst.getMemoryProxy()
        self._motion = burst.getMotionProxy()
        self._events = set()
        self._deferreds = []
        
        # we do memory.getListData once per self.update, in one go.
        # later when this is done with shared memory, it will be changed here.
        # initialize these before initializing objects that use them (Ball etc.)
        self._vars_to_getlist_set = set()
        self._vars_to_getlist = []
        self.vars = {} # no leading underscore - meant as a public interface (just don't write here, it will be overwritten every update)
        self._shm = None

        # try using shared memory to access variables
        if World.isRealNao:
            SharedMemoryReader.tryToInitMMap()
            if SharedMemoryReader.isMMapAvailable():
                print "world: using SharedMemoryReader"
                self._shm = SharedMemoryReader()
                self._shm.open()
                self.vars = self._shm.vars
                self._updateMemoryVariables = self._updateMemoryVariablesFromSharedMem
        if self._shm is None:
            print "world: using ALMemory"

        self.time = time()
        self.const_time = self.time     # construction time

        joints = self._motion.getBodyJointNames()
        chains = ['Head', 'LArm', 'RArm', 'LLeg', 'RLeg']
        self.jointnames = joints
        self.chainnames = chains

        self._recorded_vars = self.getRecorderVariableNames()

        print "world will record (if asked) %s vars" % len(self._recorded_vars)
        self._recorded_header = self._recorded_vars
        self._record_basename = World.isRealNao and '/media/userdata' or '/tmp'

        # Stuff that we prefer the users use directly doesn't get a leading underscore
        self.ball = Ball(self)
        self.bglp = GoalPost(self, 'BGLP', EVENT_BGLP_POSITION_CHANGED)
        self.bgrp = GoalPost(self, 'BGRP', EVENT_BGRP_POSITION_CHANGED)
        self.yglp = GoalPost(self, 'YGLP', EVENT_YGLP_POSITION_CHANGED)
        self.ygrp = GoalPost(self, 'YGRP', EVENT_YGRP_POSITION_CHANGED)
        self.robot = Robot(self)
        self.falldetector = FalldownDetector(self)
        # construct team after all the posts are constructed, it keeps a reference to them.
        self.team = Team(self)
        self.computed = Computed(self)

        # all objects that we delegate the event computation and naoqi interaction to.
        # TODO: we have the exact state of B-HUMAN, so we could use exactly their solution,
        # and hence this todo. We have multiple objects that calculate their events
        # based on ground truths (naoqi proxies) and on calculated truths. We need to
        # rerun them every time something is updated, *in the correct order*. So right
        # now I'm hardcoding this by using an ordered list of lists, but later this
        # should be calculated by storing a "needed" and "provided" list, just like B-HUMAN,
        # and doing the sorting once (and that value can be cached to avoid recomputing on
        # each run).
        self._objects = [
            # All basic objects that rely on just naoproxies should be in the first list
            [self.ball, self.bglp, self.bgrp, self.yglp, self.ygrp,
             self.robot, self.falldetector],
            # anything that relies on basics but nothing else should go next
            [self],
            # self.computed should always be last
            [self.computed],
        ]

        if self.isRealNao:
            self.createMmapVariablesFile()
    
    def createMmapVariablesFile(self):
        """
        create the MMAP_VARIABLES_FILENAME - must have self._vars_to_getlist
        ready, so call this after __init__ is done or at its end.
        """
        
        if not os.path.exists(MMAP_VARIABLES_FILENAME):
            print ("I see %s is missing. creating it for you. it has %s variables"
                    % (MMAP_VARIABLES_FILENAME, len(self._vars_to_getlist)))
            fd = open(MMAP_VARIABLES_FILENAME, 'w+')
            fd.write('\n'.join(self._vars_to_getlist))
            fd.close()

    def calc_events(self, events, deferreds):
        """ World treats itself as a regular object by having an update function,
        this is called after the basic objects and before the computed object (it
        may set some events / variables needed by the computed object)
        """
        if self.bglp.seen and self.bgrp.seen:
            events.add(EVENT_ALL_BLUE_GOAL_SEEN)
        if self.yglp.seen and self.ygrp.seen:
            events.add(EVENT_ALL_YELLOW_GOAL_SEEN)

    def addMemoryVars(self, vars):
        # slow? but keeps the order of that of the registration
        for v in vars:
            if v not in self._vars_to_getlist_set:
                self._vars_to_getlist.append(v)
                self._vars_to_getlist_set.add(v)
                self.vars[v] = None

    def removeMemoryVars(self, vars):
        """ IMPORTANT NOTICE: you must make sure you don't remove variables that
        another object has added before, or you will probably break it
        """
        for v in vars:
            if v in self._vars_to_getlist_set:
                self._vars_to_getlist.remove(v)
                self._vars_to_getlist_set.remove(v)
                del self.vars[v]

    def getVars(self, vars, returnNoneOnMissing=True):
        """ quick access to multiple vars (like memory.getListData, only doesn't go to the
        network or anything). notice the returnNoneOnMissing bit
        """
        if returnNoneOnMissing:
            return [self.vars.get(k, None) for k in vars]
        return [self.vars[k] for k in vars]

    def _updateMemoryVariablesFromSharedMem(self):
        self._shm.update()

    #@timeit('al update time = %s ms')
    def _updateMemoryVariablesFromALMemory(self):
        # TODO: optmize the heck out of this. Options include:
        #  * subscribeOnData / subscribeOnDataChange
        #  * module with alfastmemoryaccess, and shared memory with python
        vars = self._vars_to_getlist
        values = self._memory.getListData(vars)
        for k, v in zip(vars, values):
            self.vars[k] = v

    _updateMemoryVariables = _updateMemoryVariablesFromALMemory

    def update(self, cur_time):
        self.time = cur_time
        self._updateMemoryVariables() # must be first in update
        self._doRecord()
        # TODO: automatic calculation of event dependencies (see constructor)
        for objlist in self._objects:
            for obj in objlist:
                obj.calc_events(self._events, self._deferreds)

    def getEventsAndDeferreds(self):
        events, deferreds = self._events, self._deferreds
        self._events = set()
        self._deferreds = []
        return events, deferreds

    # record robot state 
    def startRecordAll(self, filename):
        import csv
        import gzip

        self.addMemoryVars(self._recorded_vars)
        self._record_file_name = '%s/%s.csv.gz' % (self._record_basename, filename)
        self._record_file = gzip.open(self._record_file_name, 'a+')
        self._record_csv = csv.writer(self._record_file)
        self._record_csv.writerow(self._recorded_header)
        self._record_line_num = 0
    
    def _doRecord(self):
        if not self._record_csv: return
        # actuators and sensors for all dcm values
        self._record_csv.writerow(self.getVars(self._recorded_vars))
        self._record_line_num += 1
        if self._record_line_num % 10 == 0:
            print "(%3.3f) written csv line %s" % (self.time - self.const_time, self._record_line_num)

    def stopRecord(self):
        if self._record_file:
            print "file stored in %s, writing to disk (closing file).." % self._record_file_name
            sys.stdout.flush()
            self._record_file.close()
            print "done"
            sys.stdout.flush()
        self._record_file = None
        self._record_csv = None
        self.removeMemoryVars(self._recorded_vars)
