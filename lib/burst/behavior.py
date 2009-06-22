'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import (BurstDeferred, Nameable, succeedBurstDeferred,
    func_name)
import burst.moves.poses as poses

# TODO REFACTOR. A lot of the functionality of BehaviorActions but more
# specifically BehaviorEventManager is actually in EventManager / BurstDeferredMaker
# and should be reused. Still, the implementation here is highly coupled to
# a single Behavior (the whole stop/start thing). Needs some thinking.

def behaviorwrapbd(behavior_actions, f):
    def wrapper(*args, **kw):
        bd = f(*args, **kw)
        #print "behaviorwrapbd: %s" % bd
        behavior_actions._addBurstDeferred(bd)
        return bd
        # TODO - I want to return the chained bd, but some functions (actions.kick)
        # return a Behavior, and it cannot be replaced by a BD - what to do?
        #return bd.onDone(lambda _,f=f, behavior=behavior_actions._behavior, args=args, kw=kw:
        #        behavior._applyIfNotStopped(f, args, kw))
    wrapper.func_name = f.func_name
    wrapper.func_doc = f.func_doc
    return wrapper

# Wrappers to make sure that stopped state automatically witholds any
# callbacks from the Behavior.
# Interface is to use the standard actions and eventmanager interfaces.
#  - no change at all in Behavior's
# Implementation has many options:
#  - __getattr__ + decorator "returnsbd", check if this is a "bd returner" and if so wrap it and return wrapper
#   + relatively straight forward
#   + adds another layer in callchain
#  - hold a "current behavior" variable, which needs to get updated
#   have the action itself add a check for stop before even executing, and also after returning (onDone)
#   + very clean
#   - more code, where do I set the current behavior, when do I set the current behavior?
class BehaviorActions(object):
    """ See longer doc string on BehaviorEventManager. This handles the BurstDeferreds
    returned from Actions
    """

    def __init__(self, actions, behavior):
        self._actions = actions
        self._behavior = behavior
        self._bds = []
        self.verbose = True # TODO, options

    def clearFutureCallbacks(self):
        """ cancel all pending burst deferreds callbacks """
        # TODO - clear becomes cancel - is that ok?
        if self.verbose:
            print "BA.clearFutureCallbacks: removing %s" % (len(self._bds))
        for bd in self._bds:
            bd.clear()

    def _addBurstDeferred(self, bd):
        self._bds.append(bd)

    def __getattr__(self, k):
        actions_k = getattr(self._actions, k)
        if hasattr(actions_k, 'returnsbd'):
            return behaviorwrapbd(self, actions_k)
        return actions_k
                
class BehaviorEventManager(object):
    """ Manage all calls to EventManager for a specific Behavior.

    The main purpose is to easily do stopping and restarting of the behavior.

    The behavior must still implement the _start to register all events,
    but the _stop can be avoided in the simpler cases, where all the behavior
    does is governed by callbacks on events, call-laters or actions.

    The BEM will record all callbacks and calllaters and unregister/cancel them
    when the behavior is stopped.
    """

    def __init__(self, eventmanager, behavior):
        self._eventmanager = eventmanager
        self._behavior = behavior
        self._cb_to_wrapper = {}
        self._registered = set() # try to avoid this becoming too big
        self._calllaters = [] # TODO (small, Algorithmic) - this is currently suboptimal on clear. (O(N))
        self.verbose = True # TODO, options

    def clearFutureCallbacks(self):
        """ cancel callbacks, event registrations """
        for cb in self._calllaters:
            self._eventmanager.cancelCallLater(cb)
        for cb, event in self._registered:
            self._eventmanager.unregister(cb, event)
        if self.verbose:
            print "BEM.clearFutureCallbacks: removing %s, %s" % (len(self._calllaters), len(self._registered))
        del self._calllaters[:]
        self._registered.clear()
        self._cb_to_wrapper.clear()

    def register(self, cb, event):
        wrapper = lambda: self._behavior._applyIfNotStopped(cb, [], {})
        self._cb_to_wrapper[cb] = wrapper
        self._eventmanager.register(wrapper, event)
        self._registered.add((wrapper, event))

    def register_oneshot(self, callback, event):
        wrapper = lambda: self._behavior._applyIfNotStopped(cb, [], {})
        self._cb_to_wrapper[cb] = wrapper
        self._eventmanager.register_oneshot(wrapper, event)

    def unregister(self, callback, event=None):
        if callback not in self._cb_to_wrapper: return
        self._eventmanager.unregister(self._cb_to_wrapper[callback], event)
        # TODO - remove from self? nah, who cares?
        # we cannot delete.. may be multiple events.
        # TODO: could solve this with reference counting. But is this really a problem?
        #del self._cb_to_wrapper[cb]

    def callLater(self, dt, callback, *args, **kw):
        def wrapper(*args, **kw):
            #print "BEM %s wrapper" % (self._behavior.name)
            return self._behavior._applyIfNotStopped(callback, args, kw)
        self._cb_to_wrapper[callback] = wrapper 
        self._eventmanager.callLater(dt, callback, *args, **kw)

    def callLaterBD(self, dt):
        """ returns a BurstDeferred which is called in dt seconds """
        bd = self._eventmanager.burst_deferred_maker.make(self)
        self.callLater(dt, bd.callOnDone)
        return bd

    def cancelCallLater(self, callback):
        if callback not in self._cb_to_wrapper: return
        self._eventmanager.cancelCallLater(self._cb_to_wrapper[callback])

    def __getattr__(self, k):
        # everything else goes to eventmanager directly
        return getattr(self._eventmanager, k)

class Behavior(BurstDeferred, Nameable):

    def __init__(self, actions, name, *args, **kw):
        """  Note to inheriting folk: this constructor must be the /last/
        call in your constructor, since it calls your start method
        """
        BurstDeferred.__init__(self, self, *args, **kw)
        Nameable.__init__(self, name)
        self._actions = BehaviorActions(actions, self)
        self._world = actions._world
        self._eventmanager = BehaviorEventManager(actions._eventmanager, self)
        self._make = self._eventmanager.burst_deferred_maker.make
        self._succeed = self._eventmanager.burst_deferred_maker.succeed
        self._bd = None # if we are waiting on a single bd, this should be it. If we are waiting on more - split behavior?
        self._stopped = True

    def _applyIfNotStopped(self, f, args, kw):
        if self.stopped():
            print "%s, %s: Who is calling me at this time? I am stopped" % (self, func_name(f))
            return
        return apply(f, args, kw)

    def stop(self):
        """ Doesn't call any callbacks (by convention), so safe to call first when overriding """
        if self._stopped: return self._succeed(self)
        if self._bd:
            self._bd.clear()
            self._bd = None
        self._stopped = True
        self._eventmanager.clearFutureCallbacks()
        self._actions.clearFutureCallbacks()
        return self._stop() # User cb - should return a BurstDeferred.

    def stopped(self):
        return self._stopped

    def start(self):
        if not self._stopped: return self
        self._stopped = False
        self._start(firstTime=True)
        return self

    def log(self, msg):
        print "%s: %s" % (self.__class__.__name__, msg)

    #####  Override by Inheritance  #####

    def _start(self, firstTime=False):
        pass # defaults to empty behavior

    def _stop(self):
        """ Behavior specific burstdeferred fired on stop completion, allows
        you to stop any child behaviors """
        return self._succeed(self)

    def __str__(self):
        return '<Behavior %s: %s>' % (self.name, self.toCondensedString())

    __repr__ = __str__

class ContinuousBehavior(Behavior):
    
    def __init__(self, actions, name):
        super(ContinuousBehavior, self).__init__(actions=actions, name=name, allow_chaining=False)

    def onDone(self, cb):
        #import pdb; pdb.set_trace()
        raise RuntimeError("You cannot register an onDone callback on a continuous behavior.")

class InitialBehavior(Behavior):
    
    def __init__(self, actions, name, initial_pose=poses.INITIAL_POS):
        super(InitialBehavior, self).__init__(actions=actions, name=name)
        self._initial_pose = initial_pose

    def stop(self):
        if not self.stopped():
            print "Stopping %s" % (self.name)
        return super(InitialBehavior, self).stop()

