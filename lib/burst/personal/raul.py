""" Personal file for a robot by the name of this file.

PLEASE PAY ATTENTION TO THE FOLLOWING:

There is the good way to update stuff, and the bad way (asaf, I'm looking at you).

# BAD
import moves.walks as walks
walks.SIT_POS = [2,3,4]

# GOOD
import moves.walks as walks
walks.SIT_POS[:] = [2,3,4]

# ALSO GOOD
walks.SIT_POS[2] = 10

"""

import burst

import burst.moves.walks as walks
walks.STRAIGHT_WALK.defaultSpeed = 90

import burst.behavior_params as params
params.KICK_X_MIN[:] = [14,14]
params.KICK_X_MAX[:] = [18,18]
params.KICK_Y_MIN[:] = [4.0,-2.5]
params.KICK_Y_MAX[:] = [6.0,-4.5]

####### UGLY CHANGE, RAUL ONLY, FAULTY JOINT #########
# I have two different sets of proxies, and it is a pain
# to make them both take the same path somehow, so I'm
# patching both.
# - alon

def raulSetBodyStiffness(realproxy, orig_setbodystiffness, num):
    # set everything except the faulty arm
    d = orig_setbodystiffness(num)
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
