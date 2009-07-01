""" Personal file for a robot by the name of this file. """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [14,14]
params.KICK_X_MAX = [20,20]
params.KICK_Y_MIN = [4.5,-3.5]
params.KICK_Y_MAX = [9.25,-8]

## Choreograph moves
import burst.moves.choreograph as choreograph
(jointCodes, angles, times) = choreograph.CIRCLE_STRAFE_CLOCKWISE
angles[jointCodes.index("RHipRoll")][1] = -0.21642
(jointCodes, angles, times) = choreograph.CIRCLE_STRAFE_COUNTER_CLOCKWISE
angles[jointCodes.index("LHipRoll")][1] = 0.235

## General moves
import burst.moves.poses as poses
poses.STRAIGHT_WALK_INITIAL_POSE = [
                (poses.HEAD_POS_FRONT_BOTTOM,
                 (1.7655921000000001, 0.27914604999999998, -1.558586, -0.50157607000000004),
                 (0.010779962000000001, -0.047512039999999998, -0.57214003999999996, 1.0384761, -0.52160196999999997, 0.042993963000000003),
                 (0.010779962000000001, 0.039925963000000002, -0.58449596000000004, 1.0308900000000001, -0.51845001999999996, -0.041376039000000003),
                 (1.7380640999999999, -0.25468596999999998, 1.5615699999999999, 0.54307795000000003),
                 1.0),
                ]

## Walks
from .. import walkparameters; WalkParameters = walkparameters.WalkParameters
import burst.moves.walks as walks
from burst_consts import DEG_TO_RAD

#walks.STRAIGHT_WALK.defaultSpeed = 130
walks.SIDESTEP_WALK.defaultSpeed = 27 # 20 seems just fine

# SLOW WALK
#walks.FIRST_TWO_SLOW_STEPS = True
#walks.STRAIGHT_WALK = walks.Walk('STRAIGHT_WALK raul', WalkParameters([
#           100.0 * DEG_TO_RAD, # ShoulderMedian
#           15.0 * DEG_TO_RAD,  # ShoulderAmplitude
#           30.0 * DEG_TO_RAD,  # ElbowMedian
#           10.0 * DEG_TO_RAD,  # ElbowAmplitude
#           4.5,                   # LHipRoll(degrees)
#           -4.5,                  # RHipRoll(degrees)
#           0.22,                  # HipHeight(meters)
#           3.4,                   # TorsoYOrientation(degrees)
#           0.070,                  # StepLength
#           0.043,                  # StepHeight
#           0.03,                  # StepSide
#           0.3,                   # MaxTurn
#           0.01,                  # ZmpOffsetX
#           0.00]),                  # ZmpOffsetY
#           80          # 20ms count per step
#    )

import burst.moves.poses as poses
"""
#Probably no need when arm is OK.
#poses.GREAT_KICK_LEFT_OFFSET = poses.moveDegToRad((
    #Stand up more fully
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #swing to the right
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,-3.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #lift the left leg
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,-3.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #Get ready
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,-3.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #Kick
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,-3.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #make leg go further away
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,-3.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #lift the left leg
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,-3.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #swing to the right
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0),
    #Stand up more fully
    ((0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0,0.0,0.0),
     (0.0,0.0,0.0,0.0),0.0)
))
"""
####### UGLY CHANGE, RAUL ONLY, FAULTY JOINT #########
# I have two different sets of proxies, and it is a pain
# to make them both take the same path somehow, so I'm
# patching both.
# - alon

#from twisted.python import log
#import burst

#def raulSetBodyStiffness(realproxy, orig_setbodystiffness, num):
#    # set everything except the faulty arm
#    d = orig_setbodystiffness(num)
#    if num > 0.0:
#        realproxy.setJointStiffness('LShoulderRoll', 0.0)
#    return d
#
#orig_getMotionProxy = burst.getMotionProxy
#
#def getRaulMotionProxy(deferred=True):
#
#    class RaulMotionProxy(object):
#
#        def __init__(self, deferred):
#            self._p = orig_getMotionProxy(deferred)
#            self._orig_setbodystiffness = self._p.setBodyStiffness
#
#        def setBodyStiffness(self, num):
#            return raulSetBodyStiffness(self._p, #self._orig_setbodystiffness, num)
#
#        def __getattr__(self, k):
#            return getattr(self._p, k)
#
#    return RaulMotionProxy(deferred)
#
#burst.getMotionProxy = getRaulMotionProxy

#if burst.using_pynaoqi:
#    import pynaoqi
#    # Really, Really UGLY
#    def new_init(self, *args, **kw):
#        pynaoqi.NaoQiConnection.__init__(self, *args, **kw)
#        # we should be the first callback, this is crucial
#        self.modulesDeferred.addCallback(lambda result: #setup_stiffness_method(self)).addErrback(log.err)
#    def setup_stiffness_method(self):
#        import types
#        orig_setBodyStiffness = self.ALMotion.setBodyStiffness
#        self.ALMotion.setBodyStiffness = types.MethodType(
#            lambda self, num: raulSetBodyStiffness(self, #orig_setBodyStiffness, num), self.ALMotion)
#    #pynaoqi.NaoQiConnection.__init__ = new_init
#
#    # oh, and we need to patch the getDefaultConnection too / only
#    con = pynaoqi.getDefaultConnection()
#    con.modulesDeferred.addCallback(lambda result: setup_stiffness_method#(con)).addCallback(log.err)

#print """
#RAUL HAS A FAULTY ARM. PATCHED ALMotion.setBodyStiffness
#to not set stiffness on it.  If you really want to set it's
#stiffness, use setChainStiffness or setJointStiffness, they
#remain unpatched.
#"""
