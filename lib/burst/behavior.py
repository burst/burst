'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import BurstDeferred, Nameable, succeedBurstDeferred
import burst.moves.poses as poses

def checkstopped(f):
    """ used by Behavior.register """
    def wrapper(self, *args, **kw):
        if self.stopped:
            return
        return f(self, *args, **kw)
    # TODO - correct for im_func
    #wrapper.func_name = f.func_name
    #wrapper.func_doc = f.func_doc
    return wrapper

def behaviorwrapbd(behavior, f):
    def wrapper(*args, **kw):
        bd = f()
        return bd.onDone(lambda _,f=f, behavior=behavior, args=args, kw=kw:
                behavior._applyIfNotStopped(f, args, kw))
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

    def __init__(self, actions, behavior):
        self._actions = actions
        self._behavior = behavior

    def __getattr__(self, k):
        actions_k = getattr(self._actions, k)
        if hasattr(actions_k, 'returnsbd'):
            return behaviorwrapbd(self._behavior, actions_k)
        return actions_k
                
class BehaviorEventManager(object):

    def __init__(self, eventmanager, behavior):
        self._eventmanager = eventmanager
        self._behavior = behavior
        self._cb_to_wrapper = {}

    def register(self, cb, event):
        wrapper = lambda: self._behavior._applyIfNotStopped(cb, [], {})
        self._cb_to_wrapper[cb] = wrapper
        self._eventmanager.register(wrapper, event)

    def register_oneshot(self, callback, event):
        wrapper = lambda: self._behavior._applyIfNotStopped(cb, [], {})
        self._cb_to_wrapper[cb] = wrapper
        self._eventmanager.register_oneshot(wrapper, event)

    def unregister(self, callback, event=None):
        if callback not in self._cb_to_wrapper: return
        self._eventmanager.unregister(self._cb_to_wrapper[callback], event)
        # we cannot delete.. may be multiple events.
        # TODO: could solve this with reference counting. But is this really a problem?
        #del self._cb_to_wrapper[cb]

    def callLater(self, dt, callback, *args, **kw):
        wrapper = lambda *args, **kw: self._behavior._applyIfNotStopped(callback, args, kw)
        self._cb_to_wrapper[callback] = wrapper 
        self._eventmanager.callLater(dt, callback, args, kw)

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

    def __init__(self, actions, name):
        """  Note to inheriting folk: this constructor must be the /last/
        call in your constructor, since it calls your start method
        """
        BurstDeferred.__init__(self, self)
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
            print "%s: Who is calling me at this time? I am stopped" % self
            return
        return apply(f, args, kw)

    def stop(self):
        """ Doesn't call any callbacks (by convention), so safe to call first when overriding """
        if self._stopped: return self._succeed(self)
        if self._bd:
            self._bd.clear()
            self._bd = None
        self._stopped = True
        return self._stop_complete()

    def stopped(self):
        return self._stopped

    def start(self):
        if not self._stopped: return
        self._stopped = False
        self._start(firstTime=True)

    #####  Override by Inheritance  #####

    def _start(self, firstTime=False):
        pass # defaults to empty behavior

    def _stop_complete(self):
        """ Behavior specific burstdeferred fired on stop completion, allows
        you to stop any child behaviors """
        return self._succeed(self)

    def __str__(self):
        return '<Behavior %s: %s>' % (self.name, self.toCondensedString())

    __repr__ = __str__

class ContinuousBehavior(Behavior):
    
    def onDone(self, cb):
        raise RuntimeException("You cannot register an onDone callback on a continuous behavior.")

class InitialBehavior(Behavior):
    
    def __init__(self, actions, name, initial_pose=poses.INITIAL_POS):
        super(InitialBehavior, self).__init__(actions=actions, name=name)
        self._initial_pose = initial_pose

