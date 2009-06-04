"""
Units:
 Angles - radians
 Lengths - cm
"""

from time import time
import datetime
import csv
import os
import stat
import sys
import mmap
import struct
import linecache

import burst
from ..events import (EVENT_ALL_BLUE_GOAL_SEEN, EVENT_ALL_YELLOW_GOAL_SEEN,
    EVENT_BGLP_POSITION_CHANGED, EVENT_BGRP_POSITION_CHANGED,
    EVENT_YGLP_POSITION_CHANGED, EVENT_YGRP_POSITION_CHANGED)
from ..sensing import FalldownDetector
from burst_util import running_average, LogCalls

from sharedmemory import *
from objects import Ball, GoalPost
from robot import Robot
from team import Team
from computed import Computed
from objects import Locatable
from localization import Localization
from movecoordinator import MoveCoordinator
from kinematics import Pose
from odometry import Odometry
import burst.field as field

# TODO: Shouldn't require adding something to the path at any point
# after player_init
#sys.path.append(os.path.join(os.path.dirname(burst.__file__), '..'))
from gamecontroller import GameControllerMessage, GameController, EmptyGameController
from ..player_settings import PlayerSettings
from gamestatus import GameStatus, EmptyGameStatus

no_game_controller = False
no_game_status = False


def timeit(tmpl):
    def wrapper(f):
        def wrap(*args, **kw):
            t = time()
            ret = f(*args, **kw)
            print tmpl % ((time() - t) * 1000)
            return ret
        return wrap
    return wrapper

############################################################################

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
    # all hostnames should be lower, we just enforce it..
    hostname = fd.read().strip().lower()
    fd.close()
    return hostname

class World(object):
    """
    Main access to any information about the world around the robot,
    including other robots. Generally access is done through attributes
    that are themselves objects, such as ball, yglp, (TODO: opponent_goal,
    our_goal, teammate1, teammate2, opponent{1,2,3})
    """

    # Some variable we are sure to export if Man module (man) is
    # actually running on the robot / webots.
    MAN_ALMEMORY_EXISTANCE_TEST_VARIABLES = ['/BURST/Vision/Ball/BearingDeg']

    # TODO - move this to __init__?
    connected_to_nao = burst.connecting_to_nao()
    connected_to_webots = burst.connecting_to_webots()
    running_on_nao = burst.running_on_nao()
    hostname = gethostname()

    # TODO -use callbacks, and don't use this hardcoded list (or do?)
    jointnames = ['HeadYaw', 'HeadPitch', 'LShoulderPitch', 'LShoulderRoll',
    'LElbowYaw', 'LElbowRoll', 'LWristYaw', 'LHand', 'LHipYawPitch',
    'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll',
    'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch',
    'RAnkleRoll', 'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw',
    'RElbowRoll', 'RWristYaw', 'RHand']
    chainnames = ['Head', 'LArm', 'RArm', 'LLeg', 'RLeg']

    def __init__(self):
        if burst.options.trace_proxies:
            print "INFO: Proxy tracing is on"
            # avoid logging None objects - like when getSpeechProxy returns None
            callWrapper = lambda name, obj: (obj and LogCalls(name, obj) or obj)
        else:
            callWrapper = lambda name, obj: obj
        self._memory = callWrapper("ALMemory", burst.getMemoryProxy(deferred=True))
        self._motion = callWrapper("ALMotion", burst.getMotionProxy(deferred=True))
        self._speech = callWrapper("ALSpeech", burst.getSpeechProxy(deferred=True))
        self._leds = callWrapper("ALLeds", burst.getLedsProxy(deferred=True))
        self._events = set()
        self._deferreds = []
        
        # This makes sure stuff actually works if nothing is being updated on the nao.
        self._default_proxied_variable_value = 0.0
        
        # We do memory.getListData once per self.update, in one go.
        # later when this is done with shared memory, it will be changed here.
        # initialize these before initializing objects that use them (Ball etc.)
        default_vars = self.getDefaultVars()
        self._vars_to_get_set = set()
        self._vars_to_get_list = list()
        self.vars = {} # no leading underscore - meant as a public interface (just don't write here, it will be overwritten every update)
        self.addMemoryVars(default_vars)
        self._shm = None

        self.time = time()
        self.const_time = self.time     # construction time

        # Variables for body joint angles from dcm
        self._getAnglesMap = dict([(joint,
            'Device/SubDeviceList/%s/Position/Sensor/Value' % joint)
            for joint in self.jointnames])
        self.addMemoryVars(self._getAnglesMap.values())

        self._recorded_vars = self.getRecorderVariableNames()

        print "world will record (if asked) %s vars" % len(self._recorded_vars)
        self._recorded_header = self._recorded_vars
        self._record_basename = World.running_on_nao and '/media/userdata' or '/tmp'

        # Stuff that we prefer the users use directly doesn't get a leading
        # underscore
        #  * Vision recognized objects
        self.ball = Ball(self)
        # ULTRA MAJOR TODO: coordinate consistency. The BLUE goal is not always our
        # goal. Actually, it is so only half the time. Our system says that OUR
        # goal is at 0.0, so we should look at TEAM, see who we are, and only
        # then UPDATE THE GOALS COORDINATES.
        bglp_x, bglp_y = field.blue_goal.top_post.xy
        bgrp_x, bgrp_y = field.blue_goal.bottom_post.xy
        yglp_x, yglp_y = field.yellow_goal.top_post.xy
        ygrp_x, ygrp_y = field.yellow_goal.bottom_post.xy
        self.bglp = GoalPost('BGLP', self, EVENT_BGLP_POSITION_CHANGED, bglp_x, bglp_y)
        self.bgrp = GoalPost('BGRP', self, EVENT_BGRP_POSITION_CHANGED, bgrp_x, bgrp_y)
        self.yglp = GoalPost('YGLP', self, EVENT_YGLP_POSITION_CHANGED, yglp_x, yglp_y)
        self.ygrp = GoalPost('YGRP', self, EVENT_YGRP_POSITION_CHANGED, ygrp_x, ygrp_y)
        # TODO - other robots
        # Buttons, Leds (TODO: ultrasound, 
        self.robot = Robot(self)
        self.falldetector = FalldownDetector(self)
        # construct team after all the posts are constructed, it keeps a
        # reference to them.
        self.team = Team(self)
        # TODO - is computed used? should be renamed for legibility
        self.computed = Computed(self)
        # Self orientation and Location of self and other objects in field.
        # (passes some stuff into other objects)
        self.pose = Pose(self)
        self.localization = Localization(self)
        self.odometry = Odometry(self)

        # The Game-Status, Game-Controller and RobotData Trifecta # TODO: This is messy.
        self.playerSettings = PlayerSettings(self) # Start with the default settings. You will be configured later to the right ones by the referees.
        if no_game_status:
            self.gameStatus = EmptyGameStatus()
        else:
            self.gameStatus = GameStatus(self.playerSettings)
        if no_game_controller:
            self._gameController = EmptyGameController()
        else:
            self._gameController = GameController(self.gameStatus)

        self._movecoordinator = MoveCoordinator(self)

        # All objects that we delegate the event computation and naoqi
        # interaction to.  TODO: we have the exact state of B-HUMAN, so we
        # could use exactly their solution, and hence this todo. We have
        # multiple objects that calculate their events based on ground truths
        # (naoqi proxies) and on calculated truths. We need to rerun them
        # every time something is updated, *in the correct order*. So right
        # now I'm hardcoding this by using an ordered list of lists, but
        # later this should be calculated by storing a "needed" and
        # "provided" list, just like B-HUMAN, and doing the sorting once (and
        # that value can be cached to avoid recomputing on each run).
        self._objects = [
            # All basic objects that rely on just naoproxies should be in the
            # first list
            [self._movecoordinator,
             self.ball, self.bglp, self.bgrp, self.yglp, self.ygrp,
             self.robot, self.falldetector, self._gameController],
            [self.gameStatus],
            # anything that relies on basics but nothing else should go next
            [self],
            # self.computed should always be last
            [self.computed, self.localization],
        ]

        # logging variables
        self._logged_objects = [[obj, None] for obj in [self.ball]]
        self._object_to_filename = {self.ball: 'ball'}
        self._do_log_positions = burst.options.log_positions
        if self._do_log_positions:
            self._openPositionLogs()

        # Try using shared memory to access variables
        if World.running_on_nao:
            #self.updateMmapVariablesFile() # // TODO -remove the file! it is EVIL
            SharedMemoryReader.tryToInitMMap()
            if SharedMemoryReader.isMMapAvailable():
                print "world: using SharedMemoryReader"
                self._shm = SharedMemoryReader(self._vars_to_get_list)
                self._shm.open()
                self.vars = self._shm.vars
                self._updateMemoryVariables = self._updateMemoryVariablesFromSharedMem
        if self._shm is None:
            print "world: using ALMemory"

        self.checkManModule()

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

    # Accessors

    def getMemoryProxy(self):
        return self._memory

    def getMotionProxy(self):
        return self._motion

    def getSpeechProxy(self):
        return self._speech
    
    def getDefaultVars(self):
        """ return list of variables we want anyway, regardless of what
        the objects we use want. This currently includes:
         Device/SubDeviceList/<jointname>/Position/Sensor/Value
          - for getAngle
        """
        return ['Device/SubDeviceList/%s/Position/Sensor/Value' % joint
            for joint in self.jointnames]

    def getEventsAndDeferreds(self):
        events, deferreds = self._events, self._deferreds
        self._events = set()
        self._deferreds = []
        return events, deferreds

    # accessors that wrap the ALMemory - you can also
    # use world.vars
    def getAngle(self, jointname):
        """ almost the same as ALMotion.getAngle as the help tells it -
        returns the sensed angle, which we take to be the sensor position,
        not the actuated position
        """
        return self.vars[self._getAnglesMap[jointname]]

    # accessors that wrap ALMotion
    # TODO - cache these
    def getRemainingFootstepCount(self):
        return self._motion.getRemainingFootStepCount()

    # Utility

    def checkManModule(self):
        """ report to user if the Man module isn't loaded. Since recently Man stopped being
        logged as a module, we look for some of the variables we export.
        """
        # note - blocking
        print "Checking for Man module by getting a vision variable: %s" % self.MAN_ALMEMORY_EXISTANCE_TEST_VARIABLES
        self._memory.getListData(self.MAN_ALMEMORY_EXISTANCE_TEST_VARIABLES).addCallback(self.onCheckManModuleResults)

    def onCheckManModuleResults(self, result):
        #print "onCheckManModuleResults: %r" % (result,)
        if result[0] == 'None':
            print "WARNING " + "*"*60
            print "WARNING"
            print "WARNING >>>>>>> Man Isn't Running - naoload && naoqi restart <<<<<<<"
            print "WARNING"
            print "WARNING " + "*"*60
        else:
            print "Man found"

    # ALMemory and Shared memory functions

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
        # slow? but retains the order of the registration
        for v in vars:
            if v not in self._vars_to_get_set:
                self._vars_to_get_list.append(v)
                self._vars_to_get_set.add(v)
                self.vars[v] = self._default_proxied_variable_value

    def removeMemoryVars(self, vars):
        """ IMPORTANT NOTICE: you must make sure you don't remove variables that
        another object has added before, or you will probably break it
        """
        for v in vars:
            if v in self._vars_to_get_set:
                self._vars_to_get_list.remove(v)
                self._vars_to_get_set.remove(v)
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
        vars = self._vars_to_get_list
        self._memory.getListData(vars).addCallback(self._updateMemoryFromALMemory_onResults)

    def _updateMemoryFromALMemory_onResults(self, values):
        for k, v in zip(self._vars_to_get_list, values):
            if v == 'None':
                v = self._default_proxied_variable_value
            self.vars[k] = v

    _updateMemoryVariables = _updateMemoryVariablesFromALMemory

    # Callbacks

    def collectNewUpdates(self, cur_time):
        self.time = cur_time
        self._updateMemoryVariables() # must be first in update
        self._doRecord()
        # TODO: automatic calculation of event dependencies (see constructor)
        for objlist in self._objects:
            for obj in objlist:
                obj.calc_events(self._events, self._deferreds)
        if self._do_log_positions:
            self._logPositions()

    def cleanup(self):
        if self._do_log_positions:
            self._closePositionLogs()

    # Logging Functions

    def _openPositionLogs(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        for i, data in enumerate(self._logged_objects):
            filename = '%s_%s.csv' % (self._object_to_filename[data[0]], timestamp)
            fd = open(filename, 'w+')
            writer = csv.writer(fd)
            writer.writerow(Locatable.HISTORY_LABELS)
            data[1] = (fd, writer)
            print "LOGGING: opened %s for logging %s" % (filename, data[0])

    def _logPositions(self):
        for obj, (fd, writer) in self._logged_objects:
            if obj.history[-1] != None:
                writer.writerow(obj.history[-1])
            else:
                writer.writerow([self.time] + [0.0] * (len(Locatable.HISTORY_LABELS) - 1))

    def _closePositionLogs(self):
        for obj, (fd, writer) in self._logged_objects:
            fd.close()

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

