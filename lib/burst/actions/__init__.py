from math import atan2
import burst
from burst.consts import *
from burst_util import (transpose, cumsum, normalize2, succeed,
    BurstDeferred, Deferred, DeferredList, chainDeferreds,
    wrapDeferredWithBurstDeferred)
from burst.events import *
from burst.eventmanager import EVENT_MANAGER_DT
import burst.moves
from burst.world import World
from burst.walkparameters import WalkParameters

# Local modules
from actionconsts import *
from journey import Journey
from kicking import BallKicker
from vision import Tracker, Searcher

#######

class Actions(object):
    """ High level class used by Player to initiate any action that the robot does,
    including basics: head moves, joint moves, joint scripts (executeMoves)
    high level moves: change location relative
    vision and head moves: head tracking
    vision and head and body moves: ball kicking
    
    We put high level operations in actions if:
     * it is an easily specified operation (head scanning)
     * it is short timed (ball kicking)
    
    We will put it in Player instead if:
     * it is complex, runs for a long time.. (not very well understood)
    """

    def __init__(self, eventmanager):
        self._eventmanager = eventmanager
        self._world = world = eventmanager._world
        self._motion = world.getMotionProxy()
        self._speech = world.getSpeechProxy()
        self._joint_names = self._world.jointnames
        self._journey = Journey(self)
        self.tracker = Tracker(self)
        self.searcher = Searcher(self)

    #===============================================================================
    #    High Level - anything that uses vision
    #===============================================================================

    def kickBall(self, target_world_frame=None, target_bearing_distance=None):
        """ Kick the Ball. Returns an already initialized BallKicker instance which
        can be used to stop the current activity.
        
        If target is None it kicks towards the enemy goal (currently the Yellow - TODO).
        Otherwise target should be a location which will be used to short circuit the
        scanning process. (caller needs to supply a valid target)
        
        Kicking towards a target entails:
         * if target is default: scan for ball until found (using various strategies)
         * approach ball using different strategies (far, close)
         * kick
        
        TODO: target can be a robot name, then the kick becomes a pass. This requires
        being able to detect the location.
        TODO: have several kick types, one for passing, one for kicking towards goal.
        """
        if target_world_frame is not None:
            if target_bearing_distance is not None:
                print "ERROR: bad parameters to kickBall.. ignoring"
                return
            raise NotImplemented('ballKick can only work with target == None right now')
            target_bearing_distance = self._world.translateWorldFrameToBearingDistance(target_world_frame)
        ballkicker = BallKicker(self._eventmanager, self, target_bearing_distance=target_bearing_distance)
        ballkicker.start()
        return ballkicker

    def track(self, target, on_lost_callback=None):
        """ Track an object that is seen. If the object is not seen,
        does nothing. """
        if not self.searcher.stopped():
            raise Exception("Can't start tracking while searching")
        self.tracker.track(target, on_lost_callback=on_lost_callback)

    def search(self, targets):
        if not self.tracker.stopped():
            raise Exception("Can't start searching while tracking")
        return self.searcher.search(targets)

    def executeTracking(self, target, normalized_error_x=0.05, normalized_error_y=0.05):
        """ Do a single tracking step, aiming to center on the given target.
        Return value:
         centerd, maybe_bd
         centered - True if centered, False otherwise
         maybe_bd - a BurstDeferred if head movement initiated, else None
        """
        def location_error(target, x_error, y_error):
            # TODO - using target.centerX and target.centerY without looking at newness is broken.
            # Normalize ball X between 1 (left) to -1 (right)
            xNormalized = normalize2(target.centerX, IMAGE_HALF_WIDTH)
            # Normalize ball Y between 1 (top) to -1 (bottom)
            yNormalized = normalize2(target.centerY, IMAGE_HALF_HEIGHT)
            return (abs(xNormalized) <= normalized_error_x and
                    abs(yNormalized) <= normalized_error_y), xNormalized, yNormalized

        bd = None
        centered, xNormalized, yNormalized = location_error(target,
            normalized_error_x, normalized_error_y)
        if not centered and not self._world.robot.isHeadMotionInProgress():
            CAM_X_TO_RAD_FACTOR = FOV_X / 4 # TODO - const that 1/4 ?
            CAM_Y_TO_RAD_FACTOR = FOV_Y / 4
            deltaHeadYaw   = -xNormalized * CAM_X_TO_RAD_FACTOR
            deltaHeadPitch =  yNormalized * CAM_Y_TO_RAD_FACTOR
            #self._actions.changeHeadAnglesRelative(
            # deltaHeadYaw * DEG_TO_RAD + self._actions.getAngle("HeadYaw"),
            # deltaHeadPitch * DEG_TO_RAD + self._actions.getAngle("HeadPitch")
            # ) # yaw (left-right) / pitch (up-down)
            bd = self.changeHeadAnglesRelative(deltaHeadYaw, deltaHeadPitch)
                        # yaw (left-right) / pitch (up-down)
            #print "deltaHeadYaw, deltaHeadPitch (rad): %3.3f, %3.3f" % (
            #       deltaHeadYaw, deltaHeadPitch)
            #print "deltaHeadYaw, deltaHeadPitch (deg): %3.3f, %3.3f" % (
            #       deltaHeadYaw / DEG_TO_RAD, deltaHeadPitch / DEG_TO_RAD)
        return centered, bd

    #===============================================================================
    #    Mid Level - any motion that uses callbacks
    #===============================================================================

    def changeLocationRelative(self, delta_x, delta_y = 0.0, delta_theta = 0.0,
        walk=moves.STRAIGHT_WALK, steps_before_full_stop=0):
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
        
    def turn(self, deltaTheta, walk=moves.STRAIGHT_WALK):
        self.setWalkConfig(walk.walkParameters)
        dgens = []
        dgens.append(lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))
        
        print "ADD TURN (deltaTheta): %f" % (deltaTheta)
        dgens.append(lambda _: self._motion.addTurn(deltaTheta, DEFAULT_STEPS_FOR_TURN))
        
        duration = 1.0 # TODO - compute duration correctly
        d = chainDeferreds(dgens).addCallback(lambda _: self._motion.post.walk())
        return self.bdFromPostIdDeferred(d, kind='walk', event=EVENT_CHANGE_LOCATION_DONE, duration=duration)

    def changeLocationRelativeSideways(self, delta_x, delta_y = 0.0, walk=moves.STRAIGHT_WALK):
        """
        Add an optional addWalkSideways and StraightWalk to ALMotion's queue.
        Will fire EVENT_CHANGE_LOCATION_DONE once finished.
         
        Coordinate frame for robot is same as world: x forward, y left (z up)
        X & Y are in radians!
        
        What kind of walk is this: for simplicity we do sidewalking then walking to target 
        (we assume no orientation change is required)
        """
        
        print "changeLocationRelativeSideways (delta_x: %3.3f delta_y: %3.3f)" % (delta_x, delta_y)
        distance, distanceSideways = delta_x / CM_TO_METER, delta_y / CM_TO_METER
        did_sideways = None

        dgens = [] # deferred generators. This is the DESIGN PATTERN to collect a bunch of
                   # stuff that would have been synchronous and turn it asynchronous
                   # All lambda's should have one parameter, the result of the last deferred.
        dgens.append(lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))

        if abs(distanceSideways) >= MINIMAL_CHANGELOCATION_SIDEWAYS:
            walk = moves.SIDESTEP_WALK
        
        dgens.append(lambda _: self.setWalkConfig(walk.walkParameters))
        
        defaultSpeed = walk.defaultSpeed
        stepLength = walk[WalkParameters.StepLength] # TODO: encapsulate walk params
        
        if distance >= MINIMAL_CHANGELOCATION_X:
            print "WALKING STRAIGHT (stepLength: %3.3f distance: %3.3f)" % (stepLength, distance)
            
            # Vova trick - start with slower walk, then do the faster walk.
            slow_walk_distance = min(distance, stepLength*2)
            if World.connected_to_nao:
                dgens.append(lambda _: self._motion.addWalkStraight( slow_walk_distance, DEFAULT_STEPS_FOR_WALK ))
                dgens.append(lambda _: self._motion.addWalkStraight( distance - slow_walk_distance, defaultSpeed ))
            else:
                print "ADD WALK STRAIGHT: %f, %f" % (distance, defaultSpeed)
                dgens.append(lambda _: self._motion.addWalkStraight( distance, defaultSpeed ))

        # Avoid minor sideways walking
        if abs(distanceSideways) >= MINIMAL_CHANGELOCATION_SIDEWAYS:
            print "WALKING SIDEWAYS (%3.3f)" % distanceSideways
            did_sideways = distanceSideways
            dgens.append(lambda _: self._motion.addWalkSideways(distanceSideways, defaultSpeed))
        else:
            print "MINOR SIDEWAYS AVOIDED! (%3.3f)" % distanceSideways
            
        duration = (defaultSpeed * distance / stepLength +
                    (did_sideways and defaultSpeed or EVENT_MANAGER_DT) ) * 0.02 # 20ms steps
        print "Estimated duration: %3.3f" % (duration)
        
        d = chainDeferreds(dgens).addCallback(lambda _: self._motion.post.walk())
        return self.bdFromPostIdDeferred(d, kind='walk', event=EVENT_CHANGE_LOCATION_DONE, duration=duration)

    def initPoseAndStiffness(self):
        """ Sets stiffness, then sets initial position for body and head.
        Returns a BurstDeferred.
        """
        # TODO - BurstDeferredList? just phase out the whole BurstDeferred in favor of t.i.d.Deferred?
        bd = BurstDeferred(None)
        def doMove(_):
            DeferredList([
                self.executeHeadMove(moves.HEAD_MOVE_FRONT_FAR).getDeferred(),
                self.executeMove(moves.INITIAL_POS).getDeferred()
            ]).addCallback(lambda _: bd.callOnDone())
        self._motion.setBodyStiffness(INITIAL_STIFFNESS).addCallback(doMove)
        #self._motion.setBalanceMode(BALANCE_MODE_OFF) # needed?
        # we ignore this deferred because the STAND move takes longer
        return bd
    
    def sitPoseAndRelax(self): # TODO: This appears to be a blocking function!
        return wrapDeferredWithBurstDeferred(self.sitPoseAndRelax_returnDeferred())

    def sitPoseAndRelax_returnDeferred(self): # TODO: This appears to be a blocking function!
        dgens = []
        def removeStiffness(_):
            d = self._motion.setBodyStiffness(0)
            self._removeStiffnessDeferred = d   # XXX DEBUG Helper
            return d
        dgens.append(lambda _: self.clearFootsteps())
        dgens.append(lambda _: self.executeMove(moves.STAND).getDeferred())
        dgens.append(lambda _: self.executeMove(moves.SIT_POS).getDeferred())
        dgens.append(removeStiffness)
        self._sitpose_deferred = chainDeferreds(dgens) # XXX DEBUG Helper
        return self._sitpose_deferred
     
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

    #===============================================================================
    #    Low Level
    #===============================================================================
    
    def changeHeadAnglesRelative(self, delta_yaw, delta_pitch, interp_time = 0.15):
        #self._motion.changeChainAngles("Head", [deltaHeadYaw/2, deltaHeadPitch/2])
        return self.executeHeadMove( (((self._world.getAngle("HeadYaw")+delta_yaw,
                                        self._world.getAngle("HeadPitch")+delta_pitch),interp_time),) )

    def getAngle(self, joint_name):
        return self._world.getAngle(joint_name)

    # Kick type - one of the kick types defined in actionconsts KICK_TYPE_STRAIGHT/KICK_TYPE_PASSING/etc...
    # Kick leg - the leg used to kick
    # Kick strength - strength of the kick (between 0..1)
    def kick(self, kick_type, kick_leg, kick_strength=1):
        # TODO: Add support for kick_type/kick_leg tuple, along with kick_strength
        return self.executeMove(KICK_TYPES[(kick_type, kick_leg)])
    
    def executeMoveChoreograph(self, (jointCodes, angles, times)):
        duration = max(col[-1] for col in times)
        d = self._motion.post.doMove(jointCodes, angles, times, 1)
        return self.bdFromPostIdDeferred(d, kind='motion',
            event=EVENT_BODY_MOVE_DONE, duration=duration)
                
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

    def clearFootsteps(self):
        return self._motion.clearFootsteps()

    def moveHead(self, x, y):
        self._motion.gotoChainAngles('Head', [float(x), float(y)], 1, 1)

    def blockingStraightWalk(self, distance):
        if self._world.robot.isMotionInProgress():
            return False

        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)

        walk = moves.STRAIGHT_WALK

        self.setWalkConfig(walk.walkParameters)
        self._motion.addWalkStraight( float(distance), 100 )

        postid = self._motion.post.walk()
        self._motion.wait(postid, 0)
        return True

    def say(self, message):
        print "saying: %s" % message
        if not self._speech is None:
            self._speech.say(message)

    def lookaround(self, lookaround_type):
        return self.executeHeadMove(LOOKAROUND_TYPES[lookaround_type])

    #================================================================================
    # Choreograph moves 
    #================================================================================

    # TODO? - generate these from moves.choreograph

    def executeGettingUpBelly(self):
        return self.executeMoveChoreograph(moves.GET_UP_BELLY)

    def executeGettingUpBack(self):
        return self.executeMoveChoreograph(moves.GET_UP_BACK)

    def executeLeapLeft(self):
        return self.executeMoveChoreograph(moves.GOALIE_LEAP_LEFT)
    
    def executeLeapLeftSafe(self):
        return self.executeMoveChoreograph(moves.GOALIE_LEAP_LEFT_SAFE)

    def executeLeapRight(self):
        return self.executeMoveChoreograph(moves.GOALIE_LEAP_RIGHT)
    
    def executeLeapRightSafe(self):
        return self.executeMoveChoreograph(moves.GOALIE_LEAP_RIGHT_SAFE)

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

    #================================================================================
    # Utilities 
    #================================================================================

    def bdFromPostIdDeferred(self, d, kind, event, duration):
        """ return a BurstDeferred from a Deferred on an operation that
        results in a Post ID (any movement in ALMotion)
        """
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
