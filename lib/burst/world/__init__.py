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

from twisted.python import log

from burst_consts import (US_DISTANCES_VARNAME, is_120, opposite_color, OUR_TEAM, OPPOSING_TEAM,
    VISION_POSTS_NAMES)
import burst_consts
import burst
from burst_events import (EVENT_ALL_OUR_GOAL_SEEN, EVENT_ALL_OPPOSING_GOAL_SEEN,
    EVENT_ALL_OUR_GOAL_IN_FRAME,
    EVENT_ALL_OPPOSING_GOAL_IN_FRAME,
    )
from burst_util import running_average, LogCalls, cross, gethostname, nicefloats

from burst.deferreds import BurstDeferredMaker
import burst.field as field

from sharedmemory import *
from objects import Ball, GoalPost, Goal
from robot import Robot
from computed import Computed
from objects import Locatable
from localization import Localization
from movecoordinator import MoveCoordinator
from kinematics import Pose
from burst.odometry import Odometry

# TODO: Shouldn't require adding something to the path at any point
# after player_init
#sys.path.append(os.path.join(os.path.dirname(burst.__file__), '..'))
from gamecontroller import GameControllerMessage, GameController
from ..player_settings import PlayerSettings
from gamestatus import GameStatus


############################################################################

class World(object):
    """
    Main access to any information about the world around the robot,
    including other robots. Generally access is done through attributes
    that are themselves objects, such as ball, opposing_lp, (TODO: opponent_goal,
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
        self._sentinel = callWrapper("ALSentinel", burst.getSentinelProxy(deferred=True))
        self._speech = callWrapper("ALSpeech", burst.getSpeechProxy(deferred=True))
        self._video = callWrapper("ALVideoDevice", burst.getALVideoDeviceProxy(deferred=True))
        self._leds = callWrapper("ALLeds", burst.getLedsProxy(deferred=True))
        self._imops = callWrapper("imops", burst.getImopsProxy(deferred=True))

        if burst.options.run_sonar:
            self._sonar = callWrapper("ALSonar", burst.getSonarProxy(deferred=True))
        self._events = set()
        self._deferreds = []

        self.burst_deferred_maker = BurstDeferredMaker()

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

        self.time = 0.0
        self.start_time = time()     # construction time

        # Variables for body joint angles from dcm
        self._getAnglesMap = dict([(joint,
            'Device/SubDeviceList/%s/Position/Sensor/Value' % joint)
            for joint in self.jointnames])
        if self.connected_to_webots and is_120:
            print "World: Using ALMotion for body angles"
            self._updateBodyAngles = self._updateBodyAngles_from_ALMotion
        else:
            print "World: Using DCM for body angles"
            self._body_angles_vars = self._getAnglesMap.values()
            self._updateBodyAngles = self._updateBodyAngles_from_DCM
            self.addMemoryVars(self._body_angles_vars)
        self.body_angles = [0.0] * 26

        # Variables for Inclination angles
        self._inclination_vars = ['Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value',
            'Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value']
        self.addMemoryVars(self._inclination_vars)

        self._recorded_vars = self._getRecorderVariableNames()

        print "world will record (if asked) %s vars" % len(self._recorded_vars)
        self._recorded_header = self._recorded_vars
        self._record_basename = World.running_on_nao and '/media/userdata' or '/tmp'

        # Stuff that we prefer the users use directly doesn't get a leading
        # underscore
        #  * Vision recognized objects
        self.ball = Ball(self)
        # Goals Notes: We start at UNCONFIGURED State, we record all the variables
        # but only start using them once we configure all the goal according to our team and
        # goal color.
        our_lp_xy = field.our_goal.top_post.xy        # left is from pov of goalie looking at opponent goal.
        our_rp_xy = field.our_goal.bottom_post.xy
        opposing_lp_xy = field.opposing_goal.bottom_post.xy
        opposing_rp_xy = field.opposing_goal.top_post.xy
        self.our_goal = Goal(name='OurGoal', which_team=OUR_TEAM,
            world=self, left_name='OurLeftPost', right_name='OurRightPost',
            left_world=our_lp_xy, right_world=our_rp_xy)
        self.our_lp = self.our_goal.left
        self.our_rp = self.our_goal.right
        self.opposing_goal = Goal(name='OpposingGoal', which_team=OPPOSING_TEAM,
            world=self, left_name='OpposingLeftPost', right_name='OpposingRightPost',
            left_world=opposing_lp_xy, right_world=opposing_rp_xy)
        self.opposing_lp = self.opposing_goal.left
        self.opposing_rp = self.opposing_goal.right
        for name in VISION_POSTS_NAMES:
            self.addMemoryVars(GoalPost.getVarsForName(name))
        # TODO - other robots
        # Buttons, Leds (TODO: sonar,
        self.robot = Robot(self)
        # TODO - is computed used? should be renamed for legibility
        self.computed = Computed(self)
        # Self orientation and Location of self and other objects in field.
        # (passes some stuff into other objects)
        self.pose = Pose(self)
        self.localization = Localization(self)
        self.odometry = Odometry(self)

        # The Game-Status, Game-Controller and RobotData Trifecta # TODO: This is messy.
        self.playerSettings = PlayerSettings(self) # Start with the default settings. You will be configured later to the right ones by the referees.
        self.gameStatus = GameStatus(self, self.playerSettings)
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
             self.ball, self.our_goal, self.opposing_goal,
             self.robot, self._gameController],
            [self.gameStatus],
            # anything that relies on basics but nothing else should go next
            [self],
            # self.computed should always be last
            [self.localization],
            [self.computed],
        ]

        # logging variables
        self._logged_objects = [[obj, None] for obj in [self.ball]]
        self._object_to_filename = {self.ball: 'ball'}
        self._do_log_positions = burst.options.log_positions
        if self._do_log_positions:
            self._openPositionLogs()

        if burst.options.no_memory_updates:
            print "world: NO MEMORY UPDATES.. N-O   M-E-M-O-R-Y   U-P-D-A-T-E-S"
            self._updateMemoryVariables = self._updateMemoryVariables_noop
        else:
            # Try using shared memory to access variables
            if World.running_on_nao:
                #self.updateMmapVariablesFile() # // TODO -remove the file! it is EVIL
                SharedMemoryReader.tryToInitMMap()
                if SharedMemoryReader.isMMapAvailable():
                    print "world: using SharedMemoryReader"
                    if US_DISTANCES_VARNAME in self._vars_to_get_list:
                        self._vars_to_get_list.remove(US_DISTANCES_VARNAME)
                    self._shm = SharedMemoryReader(self._vars_to_get_list)
                    self._updateMemoryVariables = self._updateMemoryVariables_noop #(temp)
                    self._shm.openDeferred.addCallback(self._switchToSharedMemory).addErrback(log.err)
            if self._shm is None:
                print "world: using ALMemory"

        self.checkManModule()

    def _setActions(self, actions):
        self._actions = actions

    def _switchToSharedMemory(self, _):
        if set(self.vars.keys()) != set(self._shm.vars.keys()):
            num_world, num_shared = len(self.vars), len(self._shm.vars)
            print "Notice: world requested %s vars, shared memory provides %s vars. This is ok if %s > %s" % (
                num_world, num_shared, num_shared, num_world)
        self.vars = self._shm.vars
        self._updateMemoryVariables = self._updateMemoryVariablesFromSharedMem

    # ########################################
    # EventManager API
    # ########################################

    def collectNewUpdates(self, cur_time):
        if self.time == cur_time - self.start_time:
            print "TIME ERROR: World.collectNewUpdates called with the same time twice. Ignoring"
            return
        self.time = cur_time - self.start_time
        # BodyAngles Note: if using ALMotion, this completed using a deferred - meaning with twisted not
        # during this callback, so doRecord will record previous time frame values
        self._updateBodyAngles()
        self._updateMemoryVariables() # must be first in update
        self._doRecord()
        # TODO: automatic calculation of event dependencies (see constructor)
        for objlist in self._objects:
            for obj in objlist:
                obj.calc_events(self._events, self._deferreds)
        if self._do_log_positions:
            self._logPositions()
        # some debugging tests TODO - put under some flag
        if burst.options.verbose_goals: # verbose == debug in my book. ok, in this instance of life.
            g = self.opposing_goal
            if abs(g.left.bearing - g.right.bearing) < 1e-4 and self.opposing_lp.bearing != 0.0:
                import pdb; pdb.set_trace()

    def getEventsAndDeferreds(self):
        events, deferreds = self._events, self._deferreds
        self._events = set()
        self._deferreds = []
        return events, deferreds

    def cleanup(self):
        if self._do_log_positions:
            self._closePositionLogs()
        self.odometry.cleanup()

    # ########################################
    # Player API
    # ########################################

    def configure(self, our_color):
        """ called when entering CONFIGURED state """
        self.our_goal.configure(color=our_color)
        self.opposing_goal.configure(color=burst_consts.opposite_color(our_color))

    # ########################################
    # Player/Behavior API (in addition to all
    # the exported variables)
    # ########################################

    # Accessors

    def getMemoryProxy(self):
        return self._memory

    def getMotionProxy(self):
        return self._motion

    def getSpeechProxy(self):
        return self._speech

    def getALVideoDeviceProxy(self):
        return self._video

    def getImopsProxy(self):
        return self._imops

    def getDefaultVars(self):
        """ return list of variables we want anyway, regardless of what
        the objects we use want. This currently includes:
         Device/SubDeviceList/<jointname>/Position/Sensor/Value
          - for getAngle
        """
        return ['Device/SubDeviceList/%s/Position/Sensor/Value' % joint
            for joint in self.jointnames]

    # accessors that wrap the ALMemory - you can also
    # use world.vars
    def getAngle(self, jointname):
        """ almost the same as ALMotion.getAngle as the help tells it -
        returns the sensed angle, which we take to be the sensor position,
        not the actuated position
        """
        return self.vars[self._getAnglesMap[jointname]]

    def getBodyAngles(self):
        # This works for DCM, but new naoqi doesn't support DCM very well. - no bigee, we have ALMotion.getBodyAngles
        # that works fine in simulation too.
        return self.body_angles

    def getInclinationAngles(self):
        # TODO - OPTIMIZE?
        return self.getVars(self._inclination_vars)

    # accessors that wrap ALMotion
    # TODO - cache these
    def getRemainingFootstepCount(self):
        return self._motion.getRemainingFootStepCount()

    def startRecordAll(self, filename):
        import csv
        import gzip

        self.addMemoryVars(self._recorded_vars)
        self._record_file_name = '%s/%s.csv.gz' % (self._record_basename, filename)
        self._record_file = gzip.open(self._record_file_name, 'a+')
        self._record_csv = csv.writer(self._record_file)
        self._record_csv.writerow(self._recorded_header)
        self._record_line_num = 0

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

    # ALMemory and Shared memory functions

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

    def _updateMemoryVariables_noop(self):
        pass

    def _updateMemoryVariablesFromSharedMem(self):
        self._shm.update()

    #@timeit('al update time = %s ms')
    def _updateMemoryVariablesFromALMemory(self):
        # TODO: optmize the heck out of this. Options include:
        #  * subscribeOnData / subscribeOnDataChange
        #  * module with alfastmemoryaccess, and shared memory with python
        vars = self._vars_to_get_list
        self._memory.getListData(vars).addCallback(self._updateMemoryFromALMemory_onResults).addErrback(log.err)

    def _updateMemoryFromALMemory_onResults(self, values):
        for k, v in zip(self._vars_to_get_list, values):
            if v == 'None':
                v = self._default_proxied_variable_value
            self.vars[k] = v

    _updateMemoryVariables = _updateMemoryVariablesFromALMemory

    def _updateBodyAngles_from_ALMotion_onResults(self, angles):
        #print "World: updated BodyAngles: %s" % nicefloats(angles)
        self.body_angles = angles

    def _updateBodyAngles_from_ALMotion(self):
        self._motion.getBodyAngles().addCallback(self._updateBodyAngles_from_ALMotion_onResults).addErrback(log.err)

    def _updateBodyAngles_from_DCM(self):
        self.body_angles = self.getVars(self._body_angles_vars)

    # Callbacks

    def calc_events(self, events, deferreds):
        """ World treats itself as a regular object by having an update function,
        this is called after the basic objects and before the computed object (it
        may set some events / variables needed by the computed object)
        """
        # TODO - move these to the Goal objects (which already exist)
        if self.our_lp.seen and self.our_rp.seen:
            events.add(EVENT_ALL_OUR_GOAL_IN_FRAME)
        if self.opposing_lp.seen and self.opposing_rp.seen:
            events.add(EVENT_ALL_OPPOSING_GOAL_IN_FRAME)

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

    def _getRecorderVariableNames(self):
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

    def _doRecord(self):
        if not self._record_csv: return
        # actuators and sensors for all dcm values
        self._record_csv.writerow(self.getVars(self._recorded_vars))
        self._record_line_num += 1
        if self._record_line_num % 10 == 0:
            print "(%3.3f) written csv line %s" % (self.time - self.start_time, self._record_line_num)

    # Utility

    def checkManModule(self):
        """ report to user if the Man module isn't loaded. Since recently Man stopped being
        logged as a module, we look for some of the variables we export.
        """
        # note - blocking
        print "Checking for Man module by getting a vision variable: %s" % self.MAN_ALMEMORY_EXISTANCE_TEST_VARIABLES
        self._memory.getListData(self.MAN_ALMEMORY_EXISTANCE_TEST_VARIABLES).addCallback(self.onCheckManModuleResults).addErrback(log.err)

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


