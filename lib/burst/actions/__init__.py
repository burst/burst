from math import atan2, asin
from twisted.internet.defer import log

import burst
from burst_consts import *
from burst_util import (transpose, cumsum, succeed, func_name,
    Deferred, DeferredList, chainDeferreds, returnsbd, whocalledme,
    whocalledme_outofclass)
from burst_events import *
import burst.moves.choreograph as choreograph
import burst.moves.poses as poses
import burst.moves.walks as walks
from burst.world import World
from burst.walkparameters import WalkParameters
from burst.image import normalized2_image_width, normalized2_image_height

# Local modules
from actionconsts import *
from journey import Journey
from kicking import BallKicker
from headtracker import Tracker, Centerer
from searcher import Searcher
from passing import passBall
from localizer import Localizer

from burst_consts import (InitialRobotState,
    ReadyRobotState, SetRobotState, PlayRobotState,
    FinishGameState, PenalizedRobotState, UNKNOWN_PLAYER_STATUS,
    is_120)

def stopped(behaviors):
    def wrap(f):
        def wrapper(self, *args, **kw):
            not_stopped = [k for k in behaviors if not getattr(self, k).stopped]
            if len(not_stopped) > 0:
                raise Exception("Can't start %s while %s" % (func_name(f), ','.join(str(x) for x in not_stopped)))
            return f(self, *args, **kw)
        return wrapper
    return wrap

#######

any_move_allowed = set([ReadyRobotState, PlayRobotState, UNKNOWN_PLAYER_STATUS])
head_moves_allowed = any_move_allowed.union([InitialRobotState, FinishGameState])

_use_legal = False # Global (module) flag, set by MainLoop before calling onStart of robot,o
                   # and after quit initated, for initPose and for sit pose at start and end respectively.

def legal(f, group):
    """ disallow movement according to state, according to the SPL 2009 rules.
    They basically say:
     Initial - cannot move anything except head (recheck)
     Ready - do whatever you want (you have 45 seconds, but this is not enforced here - or maybe it will be, we'll see)
     Set - only head moves allowed.
     Play - anything goes
     Finished - who cares?
     Penalized - nothing at all, not even winking.
    """
    def wrapper(self, *args, **kw):
        state = self._world.robot.state
        if not _use_legal or state in group:
            return f(self, *args, **kw)
        else: # buddy, stop right here!
            print "Actions: ILLEGAL ROBOCUP MOVE: %s; turning into a calllater" % f.func_name
            return self._eventmanager.callLaterBD(self._eventmanager.dt)
    wrapper.func_doc = f.func_doc
    wrapper.func_name = f.func_name
    return wrapper

def legal_head(f):
    return legal(f, head_moves_allowed)

def legal_any(f):
    return legal(f, any_move_allowed)



# NOTE: I'm applying legal_head/legal_any only to the lower level. maybe also to higher? (i.e. kickBall)

# SPECIAL NOTE: about the decorators
#
#  returnsbd - this is applied to any method that returns a bd, except those that calls others in Actions
#     that do. It doesn't cause any action itself (just adds an attributes that says it returns a bd), but
#     that attribute is looked for by BehaviorActions, which uses it to record BD's for later clearing on Behavior.stop.
#
#  legal_any, legal_head - implement the low level prevention of illegal actions. Set to any of the low level
#     behaviors. Don't apply to higher level ones - it will just stop bugs from being discovered.

# TODO - checks for those decorators (I must have missed something)

class Actions(object):
    """ High level class used by Player to initiate any action that the robot does,
    including basics: head moves, joint moves, joint scripts (executeMoves)
    high level moves: change location relative
    vision and head moves: head tracking, searching, localizing
    vision and head and body moves: ball kicking

    We put high level operations in Actions if:
     * it is an easily specified operation (head scanning)
     * it is short timed (ball kicking)

    We will put it in Player instead if:
     * it is complex, runs for a long time.. (not very well understood)
    """

    verbose = False

    def __init__(self, eventmanager):
        self._eventmanager = eventmanager
        self._world = world = eventmanager._world
        self.burst_deferred_maker = self._world.burst_deferred_maker
        # shortcuts to BurstDeferred factory. NOTE: don't get wrapped by BehaviorActions - should they?
        self.make = self.burst_deferred_maker.make
        self.wrap = self.burst_deferred_maker.wrap
        self.succeed = self.burst_deferred_maker.succeed

        self._motion = world.getMotionProxy()
        self._speech = world.getSpeechProxy()
        #self._video = world.getALVideoDeviceProxy()
        self._imops = world.getImopsProxy()

        self._current_camera = None # This is based on our commands only - we are the only ones changing it

        self._joint_names = self._world.jointnames
        self._journey = Journey(self)
        self._movecoordinator = self._world._movecoordinator
        self.currentCamera = CAMERA_WHICH_BOTTOM_CAMERA
        self.tracker = Tracker(self)        # Please remember to stop # Todo - Locking
        self.centerer = Centerer(self)       # Please remember to stop 
        self.searcher = Searcher(self)      # all of these behaviors
        self.localizer = Localizer(self)    # when you stop the InitialBehavior. Thank you.

        self.headControllers = [self.tracker, self.centerer, self.searcher]

        # we keep track of the last head bd
        self._current_head_bd = self.succeed(self)
        self._current_motion_bd = self.succeed(self)

        # slight changes between 1.3.8 and 1.2.0
        if is_120:
            self.setWalkConfig = self.setWalkConfig_120
        else:
            self.setWalkConfig = self.setWalkConfig_138

    #===============================================================================
    #    High Level - anything that uses vision
    #===============================================================================
    # These functions are generally a facade for internal objects, currently:
    # kicking.Kicker, headtracker.Searcher, headtracker.Tracker

    @returnsbd
    def kickBall(self, target_left_right_posts, target_world_frame=None):
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
        ballkicker = BallKicker(self, target_left_right_posts=target_left_right_posts)
        ballkicker.start()
        return ballkicker

    @returnsbd
    def passBall(self, target_world_frame=None):
        passingChallange = passBall(self._eventmanager, self)
        passingChallange.start()
        return passingChallange

    def track(self, target, lostCallback=None):
        """ Track an object that is seen. If the object is not seen,
        does nothing. """
        if not self.searcher.stopped or not self.centerer.stopped:
            raise Exception("Can't start tracking while searching")
        return self.tracker.start(target=target, lostCallback=lostCallback)

    @stopped(['tracker', 'centerer'])
    @returnsbd
    def search(self, targets, center_on_targets=True, stop_on_first=False):
        if stop_on_first:
            return self.searcher.search_one_of(targets, center_on_targets)
        else:
            return self.searcher.search(targets, center_on_targets)

    # TODO: returns centered, maybe_bd - I should wrap this too, but returnsbd
    # is too inflexible.
    def executeTracking(self, target, normalized_error_x=0.05, normalized_error_y=0.05,
            return_exact_error=False):
        if not all(x.stopped for x in self.headControllers):
            raise Exception("Can't start searching while tracking")
        return self.tracker.executeTracking(target,
            normalized_error_x=normalized_error_x,
            normalized_error_y=normalized_error_y)

    @returnsbd
    def localize(self):
        return self.localizer.start() # a Behavior, hence a BurstDeferred

    #===============================================================================
    #    Mid Level - any motion that uses callbacks
    #===============================================================================

    @returnsbd
    @legal_any
    def changeLocationRelative(self, delta_x, delta_y = 0.0, delta_theta = 0.0,
        walk=walks.STRAIGHT_WALK, steps_before_full_stop=0):
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
        bearing  = atan2(delta_y, delta_x) # TODO: Shouldn't this be the other way around?

        self._current_motion_bd = self._journey.start(walk=walk,
            steps_before_full_stop = steps_before_full_stop,
            delta_theta = delta_theta,
            distance=distance, bearing=bearing)
        return self._current_motion_bd

    @returnsbd
    @legal_any
    def turn(self, deltaTheta, walk=walks.TURN_WALK):
        print walk
        self.setWalkConfig(walk.walkParameters)
        dgens = []
        dgens.append(lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))

        print "ADD TURN (deltaTheta): %f" % (deltaTheta)
        dgens.append(lambda _: self._motion.addTurn(deltaTheta, walk.defaultSpeed))

        duration = 1.0 # TODO - compute duration correctly
        d = chainDeferreds(dgens)
        self._current_motion_bd = self._movecoordinator.walk(d, duration=duration,
                            description=('turn', deltaTheta, walk))
        return self._current_motion_bd

    # TODO: Change to walkSideways()
    @returnsbd
    @legal_any
    def changeLocationRelativeSideways(self, delta_x, delta_y = 0.0, walk=walks.STRAIGHT_WALK):
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

        dgens = []  # deferred generators. This is the DESIGN PATTERN to collect a bunch of
                    # stuff that would have been synchronous and turn it asynchronous
                    # All lambda's should have one parameter, the result of the last deferred.
        dgens.append(lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))

        if abs(distanceSideways) >= MINIMAL_CHANGELOCATION_SIDEWAYS:
            walk = walks.SIDESTEP_WALK

        dgens.append(lambda _: self.setWalkConfig(walk.walkParameters))

        defaultSpeed = walk.defaultSpeed
        stepLength = walk[WalkParameters.StepLength]

        if distance >= MINIMAL_CHANGELOCATION_X:
            print "WALKING STRAIGHT (stepLength: %3.3f distance: %3.3f defaultSpeed: %3.3f)" % (stepLength, distance, defaultSpeed)

            #dgens.append(lambda _: self._motion.addWalkStraight( distance, defaultSpeed ))
            # Vova trick - start with slower walk, then do the faster walk.
            slow_walk_distance = min(distance, stepLength*2)
            if walks.FIRST_TWO_SLOW_STEPS and World.connected_to_nao:
                dgens.append(lambda _: self._motion.addWalkStraight( slow_walk_distance, DEFAULT_SLOW_WALK_STEPS ))
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
                    (did_sideways and defaultSpeed or self._eventmanager.dt) ) * 0.02 # 20ms steps
        print "Estimated duration: %3.3f" % (duration)

        d = chainDeferreds(dgens)
        self._current_motion_bd = self._movecoordinator.walk(d, duration=duration,
                    description=('sideway', delta_x, delta_y, walk))
        return self._current_motion_bd

    @returnsbd
    @legal_any
    def changeLocationArc(self, delta_x, delta_y, walk=walks.STRAIGHT_WALK):
        #handle divide by zero 
        if delta_y==0:
            return self.changeLocationRelativeSideways(delta_x, delta_y, walk)
        #calculate radius 
        #r=((y{-,+}r)**2 + x**2)**0.5
        #0= y**2 + r**2 {+/-}y*r*2 + x**2 - r**2
        #r=abs( (y**2 + x**2) / (2*y) )
        r= abs( delta_y/2 + (delta_x**2)/(2*delta_y) )

        #sin angle = y/r
        angle = asin(delta_x/r)

        if delta_y<0:
            angle=-angle           
        
        #print "Calculated radius: %f, calculated angle %f" % (r, angle)
        
        # TODO: Handle addWalkArc limitations (min/max radius)

        # TODO: Move to journey.py (???)
        dgens = []  # deferred generators. This is the DESIGN PATTERN to collect a bunch of
                    # stuff that would have been synchronous and turn it asynchronous
                    # All lambda's should have one parameter, the result of the last deferred.
        dgens.append(lambda _: self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT))
        dgens.append(lambda _: self.setWalkConfig(walk.walkParameters))
        defaultSpeed = walk.defaultSpeed
        # give radius in meters!!!
        dgens.append(lambda _: self._motion.addWalkArc( angle, r / 100. , defaultSpeed ))        

        # TODO: Calculate arc length to get possible duration (by arc_length/speed)
        duration = 10
        d = chainDeferreds(dgens)
        self._current_motion_bd = self._movecoordinator.walk(d, duration=duration,
                    description=('arc', delta_x, delta_y, walk))
        return self._current_motion_bd


    @returnsbd
    @legal_any
    def sitPoseAndRelax(self): # TODO: This appears to be a blocking function!
        self._current_motion_bd = self.wrap(self.sitPoseAndRelax_returnDeferred(), data=self)
        return self._current_head_bd

    def sitPoseAndRelax_returnDeferred(self): # TODO: This appears to be a blocking function!
        dgens = []
        def removeStiffness(_):
            if burst.options.debug:
                print "sitPoseAndRelax: removing body stiffness"
            return self._motion.setBodyStiffness(0)
        dgens.append(lambda _: self._clearFootsteps_returnDeferred())
        #dgens.append(lambda _: self.executeMove(poses.STAND).getDeferred())
        dgens.append(lambda _: self.executeMove(poses.SIT_POS).getDeferred())
        dgens.append(removeStiffness)
        return chainDeferreds(dgens)

    def setWalkConfig_120(self, param):
        """ param should be one of the walks.WALK_X """
        (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude,
            LHipRoll, RHipRoll, HipHeight, TorsoYOrientation, StepLength,
            StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY) = param[:]

        # XXX we assume the order of these configs doesn't matter, hence the
        # DeferredList - does it?
        ds = []
        ds.append(self._motion.setWalkArmsConfig( ShoulderMedian, ShoulderAmplitude,
                                            ElbowMedian, ElbowAmplitude ))
        ds.append(self._motion.setWalkArmsEnable(True))
        # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
        ds.append(self._motion.setWalkExtraConfig( LHipRoll, RHipRoll, HipHeight, TorsoYOrientation ))
        ds.append(self._motion.setWalkConfig( StepLength, StepHeight, StepSide, MaxTurn,
                                                    ZmpOffsetX, ZmpOffsetY ))

        return DeferredList(ds)

    def setWalkConfig_138(self, param):
        """ param should be one of the walks.WALK_X """
        # 1.3.8: we currently plan to use the defaults of the new TrapezoidConfig: [5.0, -5.0]
        # default walk config is : [0.035, 0.01, 0.025, 0.2, 0.23, 3.0]
        # help said: pHipHeight must be in [0.15f 0.244f]

        (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude,
            LHipRoll, RHipRoll, HipHeight, TorsoYOrientation, StepLength,
            StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY) = param[:]

        # XXX we assume the order of these configs doesn't matter, hence the
        # DeferredList - does it?
        ds = []
        ds.append(self._motion.setWalkArmsConfig( ShoulderMedian, ShoulderAmplitude,
                                            ElbowMedian, ElbowAmplitude ))
        ds.append(self._motion.setWalkArmsEnable(True))
        ds.append(self._motion.setWalkTrapezoidConfig(LHipRoll, RHipRoll))
        ds.append(self._motion.setWalkConfig( StepLength, StepHeight, StepSide, MaxTurn,
                                                    HipHeight, TorsoYOrientation ))

        return DeferredList(ds)

    def chainHeads(self, moves):
        """ chain a number of headMoves, return a burstdeferred on the last
        move. Useful for debugging, or just for sign language. see nodtester.py """
        assert(len(moves) > 0)
        bd = self.moveHead(*moves[0])
        for move in moves[1:]:
            bd = bd.onDone(lambda _, move=move: self.moveHead(*move))
        return bd

    #===============================================================================
    #    Low Level
    #===============================================================================

    def switchToTopCamera(self):
        return self.setCamera(CAMERA_WHICH_TOP_CAMERA)

    def switchToBottomCamera(self):
        return self.setCamera(CAMERA_WHICH_BOTTOM_CAMERA)

    # don't wrap - calls two wrapped routines
    @whocalledme_outofclass
    @returnsbd
    def setCamera(self, whichCamera):
        """ Set camera used, we have two: top and bottom.
        whichCamera in [burst_consts.CAMERA_WHICH_TOP_CAMERA, burst_consts.CAMERA_WHICH_BOTTOM_CAMERA]
        """
        if self._current_camera == whichCamera:
            bd = self.succeed(self)
        else:
            if whichCamera == CAMERA_WHICH_BOTTOM_CAMERA:
                print "_"*20 + "SWITCHING TO bottom CAMERA" + '_'*20
                d = self._imops.switchToBottomCamera()
            else:
                print "_"*20 + "SWITCHING TO top CAMERA" + '_'*20
                d = self._imops.switchToTopCamera()
            bd = self.wrap(d, self)
            self._current_camera = whichCamera
        return bd

    @returnsbd
    def setCameraFrameRate(self, fps):
        bd = self.make(self)
        self._eventmanager.dt = 1.0/fps # convert number of frames per second to dt
        self._imops.setFramesPerSecond(float(fps)).addCallback(lambda _: bd.callOnDone()).addErrback(log.err)
        return bd

    def changeHeadAnglesRelative(self, delta_yaw, delta_pitch, interp_time = 0.15):
        cur_yaw, cur_pitch = self._world.getAngle("HeadYaw"), self._world.getAngle("HeadPitch")
        yaw, pitch = cur_yaw + delta_yaw, cur_pitch + delta_pitch
        if burst.options.debug:
            print "changeHeadAnglesRelative: %1.2f+%1.2f=%1.2f, %1.2f+%1.2f=%1.2f" % (
                cur_yaw, delta_yaw, yaw, cur_pitch, delta_pitch, pitch)
        return self.executeHeadMove( (((yaw, pitch),interp_time),) )

    def changeHeadAnglesRelativeChained(self, delta_yaw, delta_pitch):
        if burst.options.debug:
            print "changeHeadAnglesRelativeChained: delta_yaw %1.2f, delta_pitch %1.2f" % (delta_yaw, delta_pitch)
        return self._movecoordinator.changeChainAngles("Head", [delta_yaw, delta_pitch])

    # Kick type - one of the kick types defined in actionconsts KICK_TYPE_STRAIGHT/KICK_TYPE_PASSING/etc...
    # Kick leg - the leg used to kick
    # Kick strength - strength of the kick (between 0..1)
    def kick(self, kick_type, kick_leg, kick_dist):
        # TODO: Add support for kick_type/kick_leg tuple, along with kick_strength

        # OLDER KICKING (not including passing)
        #return self.executeMove(KICK_TYPES[(kick_type, kick_leg)],
        #    description=('kick', kick_type, kick_leg, kick_strength))

        # FOR PASSING:
        originalKick = KICK_TYPES[(kick_type, kick_leg)]
        orig_value = originalKick[4][4]
        if kick_dist > 0:
            kick_dist = kick_dist / 100
            originalKick[4][4] = self.getSpeedFromDistance(kick_dist)
        bd = self.executeMove(originalKick)
        originalKick[4][4] = orig_value
        return bd

    def inside_kick(self, kick_type, kick_leg):
        return self.executeMove(KICK_TYPES[(kick_type, kick_leg)])

    def adjusted_straight_kick(self, kick_leg, kick_side_offset=1.0):
        if kick_leg==LEFT:
            return self.executeMove(poses.getGreatKickLeft(kick_side_offset), description=('kick', 'ADJUSTED_KICK', kick_leg, 1.0, kick_side_offset))
        else :
            return self.executeMove(poses.getGreatKickRight(kick_side_offset), description=('kick', 'ADJUSTED_KICK', kick_leg, 1.0, kick_side_offset))

    @legal_any
    def executeMoveChoreograph(self, (jointCodes, angles, times), whatmove):
        self._current_motion_bd = self._movecoordinator.doMove(jointCodes, angles, times, 1,
                                            description=('choreograph', whatmove))
        return self._current_motion_bd

    # TODO: combine executeMove & executeHeadMove (as in lib/pynaoqi/__init__.py)
    @legal_any
    def executeMove(self, moves, interp_type = INTERPOLATION_SMOOTH, description=('executemove',), headIncluded=True):
        """ Go through a list of body angles, works like northern bites code:
        moves is a list, each item contains:
        head (the only optional, tuple of 2), larm (tuple of 4), lleg (tuple of 6), rleg, rarm, interp_time

        interp_type - 1 for SMOOTH, 0 for Linear
        interp_time - time in seconds for interpolation

        NOTE: currently this is SYNCHRONOUS - it takes at least
        sum(interp_time) to execute.
        """
        if len(moves[0]) == 6:
            if headIncluded:
                def getangles((head, larm, lleg, rleg, rarm, interp_time)):
                    return list(head) + list(larm) + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm) + [0.0, 0.0]
                joints = self._joint_names
            else:
                def getangles((head, larm, lleg, rleg, rarm, interp_time)):
                    return list(larm) + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm) + [0.0, 0.0]
                joints = self._joint_names[2:]
        else:
            def getangles((larm, lleg, rleg, rarm, interp_time)):
                return list(larm) + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm) + [0.0, 0.0]
            joints = self._joint_names[2:]

        n_joints = len(joints)
        angles_matrix = transpose([[x for x in getangles(move)] for move in moves])
        durations_matrix = [list(cumsum(move[-1] for move in moves))] * n_joints
        #print repr((joints, angles_matrix, durations_matrix))
        self._current_motion_bd = self._movecoordinator.doMove(joints, angles_matrix, durations_matrix,
            interp_type, description = description)
        return self._current_motion_bd

    @returnsbd
    @legal_head
    def executeHeadMove(self, moves, interp_type = INTERPOLATION_SMOOTH, description=('headmove',)):
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
        #print "executeHeadMove: duration = %s" % duration
        self._current_head_bd = self._movecoordinator.doMove(
            joints, angles_matrix, durations_matrix, interp_type, description=description)
        return self._current_head_bd

    def executeSingleHeadMove(self, yaw_delta, pitch_delta, interpolation_time):
        return self.executeHeadMove( (((yaw_delta, pitch_delta), interpolation_time),) )

    def _clearFootsteps_returnDeferred(self):
        return self._motion.clearFootsteps()

    def clearFootsteps(self):
        return self.wrap(self._motion.clearFootsteps(), data=self)
#        def debugme(result):
#            import pdb; pdb.set_trace()
#        d = self._motion.clearFootsteps()
#        d.addCallback(debugme)
#        return self.wrap(d, data=self)

    def moveHead(self, x, y, interp_time=1.0):
        """ move from current yaw pitch to new values within
        interp_time time (up to limit of actuators) """
        if self.verbose:
            print "MOVE HEAD to %s, %s" % (x, y)
        return self.executeHeadMove([((float(x), float(y)), interp_time)],
            description=('movehead', x, y))

    def blockingStraightWalk(self, distance):
        if self.isMotionInProgress():
            return False

        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)

        walk = walks.STRAIGHT_WALK

        self.setWalkConfig(walk.walkParameters).add
        self._motion.addWalkStraight( float(distance), 100 )

        postid = self._motion.post.walk()
        self._motion.wait(postid, 0)
        return True

    def say(self, message):
        print "saying: %s" % message
        if not self._speech is None:
            self._speech.post.say(message)

    def lookaround(self, lookaround_type):
        return self.executeHeadMove(LOOKAROUND_TYPES[lookaround_type])


    def killAll(self):
        self._motion.killAll()

    #================================================================================
    # Choreograph moves
    #================================================================================

    # TODO? - generate these from moves.choreograph

    def executeGettingUpBelly(self):
        return self.executeMoveChoreograph(choreograph.GET_UP_BELLY, "get up belly")

    def executeGettingUpBack(self):
        return self.executeMoveChoreograph(choreograph.GET_UP_BACK, "get up back")

    def executeLeapLeft(self):
        return self.executeMoveChoreograph(choreograph.GOALIE_LEAP_LEFT, "goalie leap left")

    def executeLeapLeftSafe(self):
        return self.executeMoveChoreograph(choreograph.GOALIE_LEAP_LEFT_SAFE, "goalie leap left safe")

    def executeLeapRight(self):
        return self.executeMoveChoreograph(choreograph.GOALIE_LEAP_RIGHT, "goalie leap right")

    def executeLeapRightSafe(self):
        return self.executeMoveChoreograph(choreograph.GOALIE_LEAP_RIGHT_SAFE, "goalie leap right safe")

    def executeCircleStrafeClockwise(self):
        return self.executeMoveChoreograph(choreograph.CIRCLE_STRAFE_CLOCKWISE, "circle strafe clockwise")

    def executeCircleStrafeCounterClockwise(self):
        return self.executeMoveChoreograph(choreograph.CIRCLE_STRAFE_COUNTER_CLOCKWISE, "circle strafe clockwise")

    def executeCircleStraferInitPose(self):
        return self.executeMoveChoreograph(choreograph.CIRCLE_STRAFER_INIT_POSE, "circle strafer init pose")

    def executeTurnCW(self):
        return self.executeMoveChoreograph(choreograph.TURN_CW, "turn cw")

    def executeTurnCCW(self):
        return self.executeMoveChoreograph(choreograph.TURN_CCW, "turn ccw")

    def executeToBellyFromLeapRight(self):
        return self.executeMoveChoreograph(choreograph.TO_BELLY_FROM_LEAP_RIGHT, "to belly from leap right")

    def executeToBellyFromLeapLeft(self):
        return self.executeMoveChoreograph(choreograph.TO_BELLY_FROM_LEAP_LEFT, "to belly from leap left")

    #================================================================================
    # Private or part of the implementation - not to be called by Player
    #================================================================================

    def _initPoseAndStiffness(self, pose):
        """ Not to be called by the player, it is called during
        BasicMainLoop.preMainLoopInit, and on completion player.onStart
        is called.

        Sets stiffness, then sets initial position for body and head.
        Returns a BurstDeferred.
        """
        # TODO - BurstDeferredList? just phase out the whole BurstDeferred in favor of t.i.d.Deferred?
        bd = self.make(self)
        def doMove(_):
            if pose:
                DeferredList([
                    #self.executeHeadMove(poses.HEAD_MOVE_FRONT_FAR).getDeferred(),
                    self.executeMove(pose).getDeferred()
                ]).addCallback(lambda _: bd.callOnDone()).addErrback(log.err)
            else:
                bd.callOnDone()
        self._motion.setBodyStiffness(INITIAL_STIFFNESS).addCallback(doMove).addErrback(log.err)
        #self._motion.setBalanceMode(BALANCE_MODE_OFF) # needed?
        # we ignore this deferred because the STAND move takes longer
        return bd


    #================================================================================
    # Status checks - about on going motions
    #================================================================================

    def getCurrentHeadBD(self):
        """ return a succeed if no head move in progress, or the bd of the current
        head move, for possible onDone calls. Note that we support multiple onDone,
        just like Deferred.addCallback, so you can register additional ones here.
        """
        return self._current_head_bd

    def getCurrentMotionBD(self):
        return self._current_motion_bd


    def isMotionInProgress(self):
        return self._movecoordinator.isMotionInProgress()

    def isHeadMotionInProgress(self):
        return self._movecoordinator.isHeadMotionInProgress()

    def isWalkInProgress(self):
        return self._movecoordinator.isWalkInProgress()

    #================================================================================
    #  Utilities and things that shouldn't be here
    #================================================================================

    def getSpeedFromDistance(self,kick_dist):
        return max(0.62 * pow(kick_dist,-0.4), 0.18)

    def getAngle(self, joint_name):
        return self._world.getAngle(joint_name)

    def getArcBearing(self, delta_x, delta_y):
        if delta_y == 0:
            return 0
        #calculate radius 
        #r=((y{-,+}r)**2 + x**2)**0.5
        #0= y**2 + r**2 {+/-}y*r*2 + x**2 - r**2
        #r=abs( (y**2 + x**2) / (2*y) )      
        r= abs( delta_y/2 + (delta_x**2)/(2*delta_y) )
        #sin angle = y/r
        # resulting angle pi-central angle
        angle = asin(delta_x/r)
        if delta_y < 0:
            angle=-angle    
        return angle


