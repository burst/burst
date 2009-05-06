import burst
from burst.consts import *
from events import (EVENT_HEAD_ANGLES_DONE,
        EVENT_TURN_DONE, EVENT_CHANGE_LOCATION_DONE)
import moves
import world
from math import atan2

INITIAL_STIFFNESS  = 0.85 # TODO: Check other stiffnessesm, as this might not be optimal.
INITIAL_HEAD_PITCH = -20.0 * DEG_TO_RAD

#25 - TODO - This is "the number of 20ms cycles per step". What should it be?
DEFAULT_STEPS_FOR_TURN = 150
# Same TODO
DEFAULT_STEPS_FOR_WALK = 150

MINIMAL_CHANGELOCATION_TURN = 1e-3

class Actions(object):

    def __init__(self, world):
        self._world = world
        self._motion = burst.getMotionProxy()

    def initPoseAndStiffness(self):
        self._motion.setBodyStiffness(1.0)
        self._motion.setBalanceMode(BALANCE_MODE_OFF) # needed?
        self._motion.gotoAngle('HeadPitch', INITIAL_HEAD_PITCH, 1.0, INTERPOLATION_SMOOTH)
        self.executeMove(moves.STAND)
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        
    def sitPoseAndRelax(self):
        self.clearFootsteps()
        self.executeMove(moves.SIT_POS)
        self._motion.setBodyStiffness(0)

    def changeHeadAngles(self, delta_yaw, delta_pitch):
        #self._motion.changeChainAngles("Head", [delta_yaw, delta_pitch])
        postid = self._motion.post.gotoChainAngles("Head", [self._motion.getAngle("HeadYaw")+delta_yaw, self._motion.getAngle("HeadPitch")+delta_pitch], 0.1, INTERPOLATION_SMOOTH)
        self._world.robot.add_expected_head_post(postid, EVENT_HEAD_ANGLES_DONE)

    def gotoHeadAngles(self, yaw, pitch):
        self._motion.gotoChainAngles("Head", [yaw, pitch], 0.1, INTERPOLATION_SMOOTH)

    def setHeadAngles(self, yaw, pitch):
        self._motion.setChainAngles("Head", [yaw, pitch])

    def getAngle(self, joint_name):
        return self._motion.getAngle(joint_name)
    
    def kick(self):
        self.executeMove(moves.ALMOST_KICK)

    def turn(self, delta_theta):
        """ Add a turn to ALMotion's queue. Will fire EVENT_TURN_DONE once finished. 
        """
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)

        self._motion.addTurn(delta_theta, DEFAULT_STEPS_FOR_TURN)
        
        postid = self._motion.post.walk()
        self._world.robot.add_expected_motion_post(postid, EVENT_TURN_DONE)

    def setWalkConfig(self, param):
        """ param should be one of the moves.WALK_X """
        (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude,
            LHipRoll, RHipRoll, HipHeight, TorsoYOrientation,
            StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY) = param[:14]

        self._motion.setWalkArmsConfig( ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude )
        self._motion.setWalkArmsEnable(True)

        # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
        self._motion.setWalkExtraConfig( LHipRoll, RHipRoll, HipHeight, TorsoYOrientation )

        self._motion.setWalkConfig( StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY )
    
    def changeLocationRelative(self, delta_x, delta_y = 0.0, delta_theta = 0.0):
        """ Add an optinoal addTurn and StraightWalk to ALMotion's queue.
         Will fire EVENT_WALK_DONE once finished.
         
        What kind of walk is this: for simplicity (until projectants come
        up with something better. yeah right. ok, maybe) we do a turn, walk,
        then final turn to wanted angle.
        """
        
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)
        
        distance = (delta_x**2 + delta_y**2)**0.5 / 100 # convert cm to meter
        bearing = atan2(delta_y, delta_x)
        # Avoid turns
        if abs(bearing) < MINIMAL_CHANGELOCATION_TURN:
            self._motion.addTurn(bearing, DEFAULT_STEPS_FOR_TURN)
        
        param = moves.SLOW_WALK # FASTER_WALK / FAST_WALK
        self.setWalkConfig(param)
        steps = param[14]
        StepLength = param[8] # TODO: encapsulate walk params
        
        print "Straight walk: StepLength: %f distance: %f" % (StepLength, distance)
        # Vova trick - start with slower walk, then do the faster walk.
        self._motion.addWalkStraight( StepLength*2, DEFAULT_STEPS_FOR_WALK )
        self._motion.addWalkStraight( distance - StepLength*2, steps )

        if abs(bearing) < MINIMAL_CHANGELOCATION_TURN:
            self._motion.addTurn(delta_theta - bearing, DEFAULT_STEPS_FOR_TURN)
        
        postid = self._motion.post.walk()
        self._world.robot.add_expected_motion_post(postid, EVENT_CHANGE_LOCATION_DONE)

    def executeMove(self, moves):
        """ Go through a list of body angles, works like northern bites code:
        moves is a list, each item contains:
         larm (tuple of 4), lleg (tuple of 6), rleg, rarm, interp_time, interp_type

        interp_type - 1 for SMOOTH, 0 for Linear
        interp_time - time in seconds for interpolation

        NOTE: currently this is SYNCHRONOUS - it takes at least
        sum(interp_time) to execute.
        """
        for move in moves:
            larm, lleg, rleg, rarm, interp_time, interp_type = move
            curangles = self._motion.getBodyAngles()
            joints = curangles[:2] + [x*DEG_TO_RAD for x in list(larm)
                    + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm)
                    + [0.0, 0.0]]
            self._motion.gotoBodyAngles(joints, interp_time, interp_type)
 
    def clearFootsteps(self):
        """ NOTE: USER BEWARE. We had problems with clearFootsteps """
        #if self._motion.getRemainingFootStepCount() > 0:
        self._motion.clearFootsteps()

