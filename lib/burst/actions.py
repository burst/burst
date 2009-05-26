from math import atan2
from consts import CM_TO_METER, IMAGE_HALF_HEIGHT, IMAGE_HALF_WIDTH
import burst
from burst.consts import *
from burst_util import (transpose, cumsum, normalize2,
    BurstDeferred, Deferred, DeferredList, chainDeferreds)
from events import *
from eventmanager import EVENT_MANAGER_DT
import moves
from world import World
from walkparameters import WalkParameters

INITIAL_STIFFNESS  = 0.85 # TODO: Check other stiffnesses, as this might not be optimal.

#25 - TODO - This is "the number of 20ms cycles per step". What should it be?
if World.connected_to_nao:
    DEFAULT_STEPS_FOR_TURN = 150
    DEFAULT_STEPS_FOR_WALK = 150 # used only in real-world
    DEFAULT_STEPS_FOR_SIDEWAYS = 60
else:
    DEFAULT_STEPS_FOR_TURN = 60
    DEFAULT_STEPS_FOR_SIDEWAYS = 60

MINIMAL_CHANGELOCATION_TURN = 0.15
MINIMAL_CHANGELOCATION_SIDEWAYS = 0.005
MINIMAL_CHANGELOCATION_X = 0.01

KICK_TYPE_STRAIGHT_WITH_LEFT = 0
KICK_TYPE_STRAIGHT_WITH_RIGHT = 1
KICK_TYPES = {KICK_TYPE_STRAIGHT_WITH_LEFT: moves.GREAT_KICK_LEFT,
              KICK_TYPE_STRAIGHT_WITH_RIGHT: moves.GREAT_KICK_RIGHT}

LOOKAROUND_QUICK = 0
LOOKAROUND_FRONT = 1
LOOKAROUND_AROUND = 2
LOOKAROUND_TYPES = {LOOKAROUND_QUICK: moves.HEAD_SCAN_QUICK,
                    LOOKAROUND_FRONT: moves.HEAD_SCAN_FRONT,
                    LOOKAROUND_AROUND: moves.HEAD_SCAN_FRONT} # TODO: Add look around

#######

class Journey(object):

    """ Class used by changeLocationRelative. Breaks down a single walk
    into multiple legs. In the simplest case it acts like the old changeLocationRelative,
    i.e. does a single leg.

    The extra complication arises from doing everything in deferred mode - every call to
    a proxy is chained via addCallback.
    """

    SLOW_START_STEPS = 2 # The amount of steps one should take at a slower pace at the beginning.

    def __init__(self, actions):
        self._printQueueBeforeExecution = False
        self._actions = actions
        self._world = self._actions._world
        self._motion = self._actions._motion
        self._deferred = None
        self._distance, self._bearing, self._delta_theta = None, None, None
        self._turn = [None, None]
        self._distance_left = None
        self._time_per_steps, self._step_length = None, None
    
    def __str__(self):
        return "<Journey %3.3f distance, %3.3f bearing>" % (self._distance, self._bearing)

    def start(self, walk, steps_before_full_stop,
            distance, bearing, delta_theta):
        """ Do first leg, if the distance is smaller than threshold do final
        leg, otherwise schedule the next leg """
        self._cmds = [] # See comment on _addCommand
        self._deferred = BurstDeferred(None)
        self._distance = distance
        self._bearing = bearing
        self._delta_theta = delta_theta
        self._distance_left = self._distance
        self._turn = turn = [None, None] # for duration estimation
        #import pdb; pdb.set_trace()
        self._time_per_steps = walk.defaultSpeed
        self._step_length = step_length = walk[WalkParameters.StepLength]
        if steps_before_full_stop == 0:
            self._leg_distance = self._distance
        else:
            self._leg_distance = steps_before_full_stop * step_length
        if abs(bearing) >= MINIMAL_CHANGELOCATION_TURN:
            turn[0] = bearing
        final_turn = delta_theta - bearing
        if abs(final_turn) >= MINIMAL_CHANGELOCATION_TURN:
            turn[1] = final_turn
        # TODO - compute duration correctly for the multiple legs
        self._duration = duration = (self._time_per_steps * distance / step_length +
                    (turn[0] and DEFAULT_STEPS_FOR_TURN or EVENT_MANAGER_DT) ) * 0.02 # 20ms steps

        self._addCommand("walkconfig", lambda _: self._actions.setWalkConfig(walk.walkParameters))
        self._addCommand("support mode", lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))

        if turn[0]:
            print "Journey: Planned: addTurn %3.3f" % turn[0]
        print "Journey: Planned: Straight walk: StepLength: %3.3f distance: %3.3f est. duration: %3.3f" % (
            step_length, distance, duration)
        if turn[1]:
            print "Journey: Planned: addTurn %3.3f" % turn[1]

        # Avoid turns
        if self._turn[0]:
            self._addCommand("addTurn %3.3f" % self._turn[0],
                lambda _: self._motion.addTurn(self._turn[0], DEFAULT_STEPS_FOR_TURN))

        self.onLegComplete()

        return self._deferred

    def _addCommand(self, description, f):
        """
        we collect any call to a proxy here, for easy understanding
        since we will want to chain them (make their execution sequential)
        without resorting to breaking everything into callbacks due to the slightly
        complex nature of this function
        """
        self._cmds.append((description, f))

    def _executeAllCommands(self):
        if self._printQueueBeforeExecution:
            print "Executing Journey Queue:"
            for desc, f in self._cmds:
                print "          %s" % desc
                print "End Journey Queue"
        d = chainDeferreds([f for desc, f in self._cmds])
        self._cmds = []
        return d

    def lastLeg(self):
        # Now turn to the final angle, taking into account the turn we
        # already did
        self.addSingleLeg()
        if self._turn[1]:
            self._addCommand("addTurn %3.3f" % self._turn[1],
                lambda _: self._motion.addTurn(self._turn[1], DEFAULT_STEPS_FOR_TURN))
        self._executeAllCommands().addCallback(
            lambda _: self._motion.post.walk().addCallback(self.onLastLegPosted))

    def onLastLegPosted(self, postid):
        # final leg will call the user's callbacks
        last_leg_duration = 1.0 # TODO - duration calculation for real
        self._world.robot.add_expected_walk_post(postid,
            EVENT_CHANGE_LOCATION_DONE, last_leg_duration
                ).onDone(self.callbackAndReset)
    
    def callbackAndReset(self):
        # TODO: do I need to reset anything?
        self._deferred.callOnDone()

    def onLegComplete(self):
        if self._distance_left <= self._leg_distance:
            self.lastLeg()
        else:
            self.addSingleLeg()
            self._executeAllCommands().addCallback(
                lambda _: self._motion.post.walk().addCallback(self._onLegCompletePosted))

    def _onLegCompletePosted(self, postid):
        leg_duration = 1.0 # TODO - compute duration correctly
        self._world.robot.add_expected_walk_post(postid,
            EVENT_CHANGE_LOCATION_DONE, leg_duration).onDone(self.onLegComplete)
    
    def _addWalkStraight(self, desc_tmpl, dist, steps):
        self._addCommand(desc_tmpl % dist, lambda _: self._motion.addWalkStraight(dist, steps))

    def addSingleLeg(self):
        """ call _motion.addWalkStraight, for webots walk do a single type of walk,
        for real robot do a slow walk for SLOW_START_STEPS and then a normal walk
        """
        leg_distance = min(self._leg_distance, self._distance_left)
        if World.connected_to_nao:
            slow_walk_distance = min(leg_distance, self._step_length * self.SLOW_START_STEPS)
            normal_walk_distance = leg_distance - slow_walk_distance
            self._addWalkStraight( "slow walk: %f", slow_walk_distance, DEFAULT_STEPS_FOR_WALK )
            self._addWalkStraight( "normal walk: %f", normal_walk_distance, self._time_per_steps)
        else:
            self._addWalkStraight( "same speed: %f", leg_distance, self._time_per_steps )
        self._distance_left -= leg_distance
        if self._distance_left < 0.0:
            print "ERROR: Journey distance left calculation incorrect"
            import pdb; pdb.set_trace()
            self._distance_left = 0.0

#######

class Actions(object):

    def __init__(self, world):
        self._world = world
        self._motion = world.getMotionProxy()
        self._speech = world.getSpeechProxy()
        self._joint_names = self._world.jointnames
        self._journey = Journey(self)

    def lookaround(self, lookaround_type):
        return self.executeHeadMove(LOOKAROUND_TYPES[lookaround_type])
    
    def initPoseAndStiffness(self):
        """ Sets stiffness, then sets initial position for body and head.
        Returns a BurstDeferred.
        """
        dgens = []
        dgens.append(lambda _: self._motion.setBodyStiffness(INITIAL_STIFFNESS))
        #self._motion.setBalanceMode(BALANCE_MODE_OFF) # needed?
        # we ignore this deferred because the STAND move takes longer
        dgens.append(lambda _: DeferredList([
            self.executeSyncHeadMove(moves.HEAD_MOVE_FRONT_FAR),
            self.executeSyncMove(moves.INITIAL_POS)]))
        bd = BurstDeferred(None)
        chainDeferreds(dgens).addCallback(lambda _: bd.callOnDone())
        return bd
    
    def sitPoseAndRelax(self): # TODO: This appears to be a blocking function!
        dgens = []
        dgens.append(lambda _: self.clearFootsteps())
        dgens.append(lambda _: self.executeSyncMove(moves.STAND))
        dgens.append(lambda _: self.executeSyncMove(moves.SIT_POS))
        dgens.append(lambda _: self._motion.setBodyStiffness(0))
        return chainDeferreds(dgens)

    def changeHeadAnglesRelative(self, delta_yaw, delta_pitch, interp_time = 0.15):
        #self._motion.changeChainAngles("Head", [deltaHeadYaw/2, deltaHeadPitch/2])
        return self.executeHeadMove( (((self._world.getAngle("HeadYaw")+delta_yaw, self._world.getAngle("HeadPitch")+delta_pitch),interp_time),) )

    def getAngle(self, joint_name):
        return self._world.getAngle(joint_name)
    
    def kick(self, kick_type):
        return self.executeMove(KICK_TYPES[kick_type])
        #return self.executeMove(moves.GREAT_KICK_LEFT)
    
    def setWalkConfig(self, param):
        """ param should be one of the moves.WALK_X """
        (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude,
            LHipRoll, RHipRoll, HipHeight, TorsoYOrientation, StepLength, 
            StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY) = param[:]

        ds = []
        ds.append(self._motion.setWalkArmsConfig( ShoulderMedian, ShoulderAmplitude,
                                            ElbowMedian, ElbowAmplitude ))
        ds.append(self._motion.setWalkArmsEnable(True))

        # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
        ds.append(self._motion.setWalkExtraConfig( LHipRoll, RHipRoll, HipHeight, TorsoYOrientation ))

        ds.append(self._motion.setWalkConfig( StepLength, StepHeight, StepSide, MaxTurn,
                                                    ZmpOffsetX, ZmpOffsetY ))

        return DeferredList(ds)
    
    def changeLocationRelative(self, delta_x, delta_y = 0.0, delta_theta = 0.0,
        walk=moves.FASTEST_WALK, steps_before_full_stop=0):
        """
        Add an optional addTurn and StraightWalk to ALMotion's queue.
         Will fire EVENT_CHANGE_LOCATION_DONE once finished.
         
        Coordinate frame for robot is same as world: x forward, y left (z up)
         
        What kind of walk this is: for simplicity we do a turn, walk,
        then final turn to wanted angle.

        @param steps_before_full_stop: Each steps_before_full_stop, the robot will halt, to regain its balance.
            If the parameter is not set, or is set to 0, the robot will execute its entire journey in one go.
        """

        distance = (delta_x**2 + delta_y**2)**0.5 / 100 # convert cm to meter
        bearing  = atan2(delta_y, delta_x)

        return self._journey.start(walk=walk,
            steps_before_full_stop = steps_before_full_stop,
            delta_theta = delta_theta,
            distance=distance, bearing=bearing)


    def executeMoveChoreograph(self, (jointCodes, angles, times)):
        duration = max(col[-1] for col in times)
        d = self._motion.post.doMove(jointCodes, angles, times, 1)
        return self.bdFromPostIdDeferred(d, kind='motion',
            event=EVENT_BODY_MOVE_DONE, duration=duration)

    def bdFromPostIdDeferred(self, d, kind, event, duration):
        post_handler = {'motion': self._world.robot.add_expected_motion_post,
            'head':self._world.robot.add_expected_head_post,
            'walk':self._world.robot.add_expected_walk_post}[kind]
        bd = BurstDeferred(None)
        def onPostId(postid):
            if not isinstance(postid, int):
                print "ERROR: onPostId with Bad PostId: %s" % repr(postid)
                print "ERROR:  Did you forget to enable ALMotion perhaps?"
                raise SystemExit
            post_handler(postid, event, duration).onDone(bd.callOnDone)
        d.addCallback(onPostId)
        return bd

    def turn(self, deltaTheta, walk=moves.FASTEST_WALK):
        self.setWalkConfig(walk.walkParameters)
        dgens = []
        dgens.append(lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))
        
        print "ADD TURN (deltaTheta): %f" % (deltaTheta)
        dgens.append(lambda _: self._motion.addTurn(deltaTheta, DEFAULT_STEPS_FOR_TURN))
        
        duration = 1.0 # TODO - compute duration correctly
        d = chainDeferreds(dgens).addCallback(lambda _: self._motion.post.walk())
        return self.bdFromPostIdDeferred(d, kind='walk', event=EVENT_CHANGE_LOCATION_DONE, duration=duration)
        

    def changeLocationRelativeSideways(self, delta_x, delta_y = 0.0, walk=moves.FASTEST_WALK):
        """
        Add an optional addWalkSideways and StraightWalk to ALMotion's queue.
        Will fire EVENT_CHANGE_LOCATION_DONE once finished.
         
        Coordinate frame for robot is same as world: x forward, y left (z up)
        X & Y are in radians!
        
        What kind of walk is this: for simplicity we do sidewalking then walking to target 
        (we assume no orientation change is required)
        """
        
        print "changeLocationRelativeSideways (delta_x: %3.3f delta_y: %3.3f)" % (delta_x, delta_y)
        distance, sideways = delta_x / CM_TO_METER, delta_y / CM_TO_METER
        did_sideways = None

        dgens = [] # deferred generators. This is the DESIGN PATTERN to collect a bunch of
                   # stuff that would have been synchronous and turn it asynchronous
                   # All lambda's should have one parameter, the result of the last deferred.
        dgens.append(lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))

#        if abs(sideways) >= MINIMAL_CHANGELOCATION_SIDEWAYS:
#            walk = moves.SIDESTEP_WALK
        
        dgens.append(lambda _: self.setWalkConfig(walk.walkParameters))
        
        steps = walk.defaultSpeed
        StepLength = walk[WalkParameters.StepLength] # TODO: encapsulate walk params
        
        if distance >= MINIMAL_CHANGELOCATION_X:
            print "WALKING STRAIGHT (StepLength: %3.3f distance: %3.3f)" % (StepLength, distance)
            
            # Vova trick - start with slower walk, then do the faster walk.
            slow_walk_distance = min(distance, StepLength*2)
            if World.connected_to_nao:
                dgens.append(lambda _: self._motion.addWalkStraight( slow_walk_distance, DEFAULT_STEPS_FOR_WALK ))
                dgens.append(lambda _: self._motion.addWalkStraight( distance - slow_walk_distance, steps ))
            else:
                print "ADD WALK STRAIGHT: %f, %f" % (distance, steps)
                dgens.append(lambda _: self._motion.addWalkStraight( distance, steps ))

        # Avoid minor sideways walking
        if abs(sideways) >= MINIMAL_CHANGELOCATION_SIDEWAYS:
            print "WALKING SIDEWAYS (%3.3f)" % sideways
            did_sideways = sideways
            dgens.append(lambda _: self._motion.addWalkSideways(sideways, DEFAULT_STEPS_FOR_SIDEWAYS))
        else:
            print "MINOR SIDEWAYS AVOIDED! (%3.3f)" % sideways
            
        duration = (steps * distance / StepLength +
                    (did_sideways and DEFAULT_STEPS_FOR_SIDEWAYS or EVENT_MANAGER_DT) ) * 0.02 # 20ms steps
        print "Estimated duration: %3.3f" % (duration)
        
        d = chainDeferreds(dgens).addCallback(lambda _: self._motion.post.walk())
        return self.bdFromPostIdDeferred(d, kind='walk',
            event=EVENT_CHANGE_LOCATION_DONE, duration=duration)

    def executeMoveRadians(self, moves, interp_type = INTERPOLATION_SMOOTH):
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
        angles_matrix = transpose([[x for x in list(larm)
                    + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm)
                    + [0.0, 0.0]] for larm, lleg, rleg, rarm, interp_time in moves])
        durations_matrix = [list(cumsum(interp_time for larm, lleg, rleg, rarm, interp_time in moves))] * n_joints
        duration = max(col[-1] for col in durations_matrix)
        #print repr((joints, angles_matrix, durations_matrix))
        d = self._motion.post.doMove(joints, angles_matrix, durations_matrix, interp_type)
        return self.bdFromPostIdDeferred(d, kind='motion', event=EVENT_BODY_MOVE_DONE, duration=duration)

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
        d = self._motion.post.doMove(joints, angles_matrix, durations_matrix, interp_type)
        return self.bdFromPostIdDeferred(d, kind='motion', event=EVENT_BODY_MOVE_DONE, duration=duration)

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
        duration = max(col[-1] for col in durations_matrix)
        d = self._motion.post.doMove(joints, angles_matrix, durations_matrix, interp_type)
        #print "executeHeadMove: duration = %s" % duration
        return self.bdFromPostIdDeferred(d, kind='head', event=EVENT_HEAD_MOVE_DONE, duration=duration)

    def executeSyncMove(self, moves, interp_type = INTERPOLATION_SMOOTH):
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
        # XXX: returns a Deferred, not a BurstDeferred - but no one expects to do anything
        # with this return value anyway. Just a hack to let Twisted do a "sitPose" nicely.
        return self._motion.doMove(joints, angles_matrix, durations_matrix, interp_type)

    def executeSyncHeadMove(self, moves, interp_type = INTERPOLATION_SMOOTH):
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
        # XXX: see executeSyncMove return comment
        return self._motion.doMove(joints, angles_matrix, durations_matrix, interp_type)
 
    def clearFootsteps(self):
        return self._motion.clearFootsteps()

    def moveHead(self, x, y):
        self._motion.gotoChainAngles('Head', [float(x), float(y)], 1, 1)

    def blockingStraightWalk(self, distance):
        if self._world.robot.isMotionInProgress():
            return False

        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)

        walk = moves.SLOW_WALK # FASTER_WALK / FAST_WALK

        self.setWalkConfig(walk.walkParameters)
        self._motion.addWalkStraight( float(distance), 100 )

        postid = self._motion.post.walk()
        self._motion.wait(postid, 0)
        return True

    def say(self, message):
        print "saying: %s" % message
        if not self._speech is None:
            self._speech.say(message)

    def executeTracking(self, target):
        if not self._world.robot.isHeadMotionInProgress():
            # Normalize ball X between 1 (left) to -1 (right)
            xNormalized = normalize2(target.centerX, IMAGE_HALF_WIDTH)
            # Normalize ball Y between 1 (top) to -1 (bottom)
            yNormalized = normalize2(target.centerY, IMAGE_HALF_HEIGHT)
            
            if abs(xNormalized) > 0.05 or abs(yNormalized) > 0.05:
                CAM_X_TO_RAD_FACTOR = 23.2/2 * DEG_TO_RAD #46.4/2
                CAM_Y_TO_RAD_FACTOR = 17.4/2 * DEG_TO_RAD #34.8/2
                deltaHeadYaw = xNormalized * CAM_X_TO_RAD_FACTOR
                deltaHeadPitch = -yNormalized * CAM_Y_TO_RAD_FACTOR
                #self._actions.changeHeadAnglesRelative(deltaHeadYaw * DEG_TO_RAD + self._actions.getAngle("HeadYaw"), deltaHeadPitch * DEG_TO_RAD + self._actions.getAngle("HeadPitch")) # yaw (left-right) / pitch (up-down)
                return self.changeHeadAnglesRelative(deltaHeadYaw, deltaHeadPitch) # yaw (left-right) / pitch (up-down)
                #print "deltaHeadYaw, deltaHeadPitch (rad): %3.3f, %3.3f" % (deltaHeadYaw, deltaHeadPitch)            
                #print "deltaHeadYaw, deltaHeadPitch (deg): %3.3f, %3.3f" % (deltaHeadYaw / DEG_TO_RAD, deltaHeadPitch / DEG_TO_RAD)                
        

    def executeGettingUpBelly(self):
        return self.executeMoveChoreograph(moves.GET_UP_BELLY)

    def executeGettingUpBack(self):
        return self.executeMoveChoreograph(moves.GET_UP_BACK)

    def executeLeapLeft(self):
        return self.executeMoveChoreograph(moves.GOALIE_LEAP_LEFT)

    def executeLeapRight(self):
        return self.executeMoveChoreograph(moves.GOALIE_LEAP_RIGHT)

    def executeCircleStrafer(self):
        return self.executeMoveChoreograph(moves.CIRCLE_STRAFER)

    def executeCircleStraferInitPose(self):
        return self.executeMoveChoreograph(moves.CIRCLE_STRAFER_INIT_POSE) 

    def executeTurnCW(self):
        return self.executeMoveChoreograph(moves.TURN_CW) 

    def executeTurnCCW(self):
        return self.executeMoveChoreograph(moves.TURN_CCW)
    
    def executeToBellyFromLeapRight(self):
        return self.executeMoveChoreograph(moves.TO_BELLY_FROM_LEAP_RIGHT)

    def executeToBellyFromLeapLeft(self):
        return self.executeMoveChoreograph(moves.TO_BELLY_FROM_LEAP_LEFT)


