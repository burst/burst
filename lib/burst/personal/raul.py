""" Personal file for a robot by the name of this file. """

import burst

import burst.moves.walks as walks
walks.STRAIGHT_WALK.defaultSpeed = 130
walks.SIDESTEP_WALK.defaultSpeed = 27 # 20 seems just fine

import burst.behavior_params as params
params.KICK_X_MIN = [14,14]
params.KICK_X_MAX = [19,19]
params.KICK_Y_MIN = [3.5,-2]
params.KICK_Y_MAX = [10.5,-9]

import burst.moves.poses as poses
#Probably no need when arm is OK.
poses.GREAT_KICK_LEFT_OFFSET = (
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
)

####### UGLY CHANGE, RAUL ONLY, FAULTY JOINT #########
# I have two different sets of proxies, and it is a pain
# to make them both take the same path somehow, so I'm
# patching both.
# - alon

def raulSetBodyStiffness(realproxy, orig_setbodystiffness, num):
    # set everything except the faulty arm
    d = orig_setbodystiffness(num)
    if num > 0.0:
        realproxy.setJointStiffness('LShoulderRoll', 0.0)
    return d

orig_getMotionProxy = burst.getMotionProxy

def getRaulMotionProxy(deferred=True):

    class RaulMotionProxy(object):

        def __init__(self, deferred):
            self._p = orig_getMotionProxy(deferred)
            self._orig_setbodystiffness = self._p.setBodyStiffness

        def setBodyStiffness(self, num):
            return raulSetBodyStiffness(self._p, self._orig_setbodystiffness, num)
        
        def __getattr__(self, k):
            return getattr(self._p, k)
    
    return RaulMotionProxy(deferred)

burst.getMotionProxy = getRaulMotionProxy

if burst.using_pynaoqi:
    import pynaoqi
    # Really, Really UGLY
    def new_init(self, *args, **kw):
        pynaoqi.NaoQiConnection.__init__(self, *args, **kw)
        # we should be the first callback, this is crucial
        self.modulesDeferred.addCallback(lambda result: setup_stiffness_method(self))
    def setup_stiffness_method(self):
        import types
        orig_setBodyStiffness = self.ALMotion.setBodyStiffness
        self.ALMotion.setBodyStiffness = types.MethodType(
            lambda self, num: raulSetBodyStiffness(self, orig_setBodyStiffness, num), self.ALMotion)
    pynaoqi.NaoQiConnection.__init__ = new_init

    # oh, and we need to patch the getDefaultConnection too / only
    con = pynaoqi.getDefaultConnection()
    con.modulesDeferred.addCallback(lambda result: setup_stiffness_method(con))

    print """

RAUL HAS A FAULTY ARM. PATCHED ALMotion.setBodyStiffness
to not set stiffness on it.  If you really want to set it's
stiffness, use setChainStiffness or setJointStiffness, they
remain unpatched.
"""
import burst.moves.choreograph as choreograph

def asafwrap(f):
    setattr(choreograph, f.func_name, f())

@asafwrap
def CIRCLE_STRAFE_CLOCKWISE():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.00000), float(-0.09250), float(-0.11868), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipRoll")
    angles.append([float(-0.08727), float(0.00698), float(0.00698), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.01745), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180), float(0.26180), float(0.26180), float(0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHand")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.08727), float(-0.10996), float(-0.10996), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipRoll")
    angles.append([float(-0.00873), float(-0.21642), float(-0.13962), float(0.00000), float(0.00000)]) # raul - 23
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])
    return jointCodes, angles, times

#CIRCLE_STRAFE_COUNTER_CLOCKWISE = mirrorChoreographMove(*CIRCLE_STRAFE_CLOCKWISE)

@asafwrap
def CIRCLE_STRAFE_COUNTER_CLOCKWISE():
    jointCodes = list()
    angles = list()
    times = list()
    suspend = 1.20000    

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)]) 
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)]) 
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.00000), float(-0.09250), float(-0.11868), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.08727), float(-0.00698), float(-0.00698), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.01745), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHand")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.08727), float(-0.10996), float(-0.10996), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.00873), float(0.235), float(0.13962), float(0.00000), float(0.00000)]) # raul elipse about 16cm for 90deg
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180), float(0.26180), float(0.26180), float(0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])
    return jointCodes, angles, times

