import burst
from burst.consts import *
from burst_util import transpose, cumsum
from events import *
from eventmanager import EVENT_MANAGER_DT
import moves
import world
from math import atan2

INITIAL_STIFFNESS  = 0.85 # TODO: Check other stiffnesses, as this might not be optimal.

#25 - TODO - This is "the number of 20ms cycles per step". What should it be?
DEFAULT_STEPS_FOR_TURN = 54

MINIMAL_CHANGELOCATION_TURN = 0.15

#######

class Actions(object):

    def __init__(self, world):
        self._world = world
        self._motion = burst.getMotionProxy()
        self._joint_names = self._motion.getBodyJointNames()

    def scanFront(self):
        # TODO: Stop move when both ball and goal found? 
        return self.executeHeadMove(moves.BOTTOM_FRONT_SCAN)

    def initPoseAndStiffness(self):
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setBalanceMode(BALANCE_MODE_OFF) # needed?
        # we ignore this deferred because the STAND move takes longer
        self.executeHeadMove(moves.BOTTOM_INIT_FAR)
        return self.executeMove(moves.STAND)
    
    def sitPoseAndRelax(self):
        self.clearFootsteps()
        self.executeMove(moves.SIT_POS)
        self._motion.setBodyStiffness(0)

    def changeHeadAnglesRelative(self, delta_yaw, delta_pitch):
        return self.executeHeadMove( (((self._motion.getAngle("HeadYaw")+delta_yaw, self._motion.getAngle("HeadPitch")+delta_pitch),0.1),) )

    def getAngle(self, joint_name):
        return self._motion.getAngle(joint_name)
    
    def kick(self):
        return self.executeMove(moves.GREAT_KICK_RIGHT)

    def setWalkConfig(self, param):
        """ param should be one of the moves.WALK_X """
        (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude,
            LHipRoll, RHipRoll, HipHeight, TorsoYOrientation,
            StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY
            ) = param[:14]

        self._motion.setWalkArmsConfig( ShoulderMedian, ShoulderAmplitude,
                                            ElbowMedian, ElbowAmplitude )
        self._motion.setWalkArmsEnable(True)

        # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
        self._motion.setWalkExtraConfig( LHipRoll, RHipRoll, HipHeight, TorsoYOrientation )

        self._motion.setWalkConfig( StepLength, StepHeight, StepSide, MaxTurn,
                                                    ZmpOffsetX, ZmpOffsetY )
    
    def changeLocationRelative(self, delta_x, delta_y = 0.0, delta_theta = 0.0,
        walk_param=moves.FASTEST_WALK):
        """
        Add an optional addTurn and StraightWalk to ALMotion's queue.
         Will fire EVENT_CHANGE_LOCATION_DONE once finished.
         
        Coordinate frame for robot is same as world: x forward, y left (z up)
         
        What kind of walk is this: for simplicity (until projectants come
        up with something better. yeah right. ok, maybe) we do a turn, walk,
        then final turn to wanted angle.
        """
        
        # TODO: No sense in setting the stiffness unless it is not yet set.
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)
        
        distance = (delta_x**2 + delta_y**2)**0.5 / 100 # convert cm to meter
        bearing  = atan2(delta_y, delta_x)
        did_a_turn = [None, None] # for duration estimation
        # Avoid turns
        if abs(bearing) >= MINIMAL_CHANGELOCATION_TURN:
            did_a_turn[0] = bearing
            self._motion.addTurn(bearing, DEFAULT_STEPS_FOR_TURN)
        
        self.setWalkConfig(walk_param)
        steps = walk_param[14]
        StepLength = walk_param[8] # TODO: encapsulate walk params
        
        # Vova trick - start with slower walk, then do the faster walk.
        slow_walk_distance = min(distance, StepLength*2)
        self._motion.addWalkStraight( slow_walk_distance, steps )
        self._motion.addWalkStraight( distance - slow_walk_distance, steps )

        # Now turn to the final angle, taking into account the turn we already did
        final_turn = delta_theta - bearing
        if abs(final_turn) >= MINIMAL_CHANGELOCATION_TURN:
            did_a_turn[1] = final_turn
            self._motion.addTurn(final_turn, DEFAULT_STEPS_FOR_TURN)
        
        duration = (steps * distance / StepLength +
                    (did_a_turn and DEFAULT_STEPS_FOR_TURN or EVENT_MANAGER_DT) ) * 0.02 # 20ms steps
        if did_a_turn[0]:
            print "DEBUG: addTurn %3.3f" % bearing
        print "DEBUG: Straight walk: StepLength: %3.3f distance: %3.3f est. duration: %3.3f" % (StepLength, distance, duration)
        if did_a_turn[1]:
            print "DEBUG: addTurn %3.3f" % final_turn
        postid = self._motion.post.walk()
        return self._world.robot.add_expected_walk_post(postid, EVENT_CHANGE_LOCATION_DONE, duration)

    def executeMove(self, moves, interp_type = INTERPOLATION_SMOOTH):
        """ Go through a list of body angles, works like northern bites code:
        moves is a list, each item contains:
         larm (tuple of 4), lleg (tuple of 6), rleg, rarm, interp_time, interp_type

        interp_type - 1 for SMOOTH, 0 for Linear
        interp_time - time in seconds for interpolation

        NOTE: currently this is SYNCHRONOUS - it takes at least
        sum(interp_time) to execute.
        """
        joints = self._joint_names[2:]
        n_joints = len(joints)
        angles_matrix = transpose([[x*DEG_TO_RAD for x in list(larm)
                    + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm)
                    + [0.0, 0.0]] for larm, lleg, rleg, rarm, interp_time in moves])
        durations_matrix = [list(cumsum(interp_time for larm, lleg, rleg, rarm, interp_time in moves))] * n_joints
        duration = max(col[-1] for col in durations_matrix)
        #print repr((joints, angles_matrix, durations_matrix))
        postid = self._motion.post.doMove(joints, angles_matrix, durations_matrix, interp_type)
        return self._world.robot.add_expected_motion_post(postid, EVENT_BODY_MOVE_DONE, duration)

    def executeHeadMove(self, moves, interp_type = INTERPOLATION_SMOOTH):
        """ Go through a list of head angles
        moves is a list, each item contains:
        head (tuple of 2), interp_time

        interp_type - 1 for SMOOTH, 0 for Linear
        interp_time - time in seconds for interpolation

        NOTE: this is ASYNCHRONOUS
        """
        joints = self._joint_names[:2]
        n_joints = len(joints)
        angles_matrix = [[angles[i] for angles, interp_time in moves] for i in xrange(n_joints)]
        durations_matrix = [list(cumsum(interp_time for angles, interp_time in moves))] * n_joints
        #print repr((joints, angles_matrix, durations_matrix))
        postid = self._motion.post.doMove(joints, angles_matrix, durations_matrix, interp_type)
        duration = max(col[-1] for col in durations_matrix)
        #print "executeHeadMove: duration = %s" % duration
        return self._world.robot.add_expected_head_post(postid, EVENT_HEAD_MOVE_DONE, duration)
 
    def clearFootsteps(self):
        """ NOTE: USER BEWARE. We had problems with clearFootsteps """
        #if self._motion.getRemainingFootStepCount() > 0:
        self._motion.clearFootsteps()

    def getToGoalieInitPosition(self):
        ids = []
        ids.append(self._motion.post.turn(90*DEG_TO_RAD, 70))
        ids.append(self._motion.post.gotoChainAngles('Head', [-90*DEG_TO_RAD, -20*DEG_TO_RAD], 1, 1))
        for x in ids:
            self._motion.wait(x, 0)


    def moveHead(self, x, y):
        self._motion.gotoChainAngles('Head', [float(x), float(y)], 1, 1)

    def blockingStraightWalk(self, distance):
        if self._world.robot.isMotionInProgress():
            return False

        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)

        param = moves.SLOW_WALK # FASTER_WALK / FAST_WALK

        self.setWalkConfig(param)
        self._motion.addWalkStraight( float(distance), 100 )

        postid = self._motion.post.walk()
        self._motion.wait(postid, 0)
        return True

