'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

import sys

from twisted.python import log

from burst_util import (BurstDeferred, Nameable, succeedBurstDeferred,
    func_name, Deferred, deferredToCondensedString, histogram_pairs)
import burst.moves.poses as poses
from burst_events import event_name

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
    wrapper.func_name = 'stoppable_' + f.func_name
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

    debug = False # TODO - options, default False

    def __init__(self, actions, behavior):
        self._actions = actions
        self._behavior = behavior
        self._bds = []
        self.verbose = True # TODO, options

    def clearFutureCallbacks(self):
        """ cancel all pending burst deferreds callbacks """
        # TODO - clear becomes cancel - is that ok?
        if self.verbose and len(self._bds) > 0:
            if len(self._bds) <= 3:
                s = ','.join(str(bd) for bd in self._bds)
            else:
                s = ','.join('%s: %s' % (num, k) for k, num
                            in histogram_pairs(map(str, self._bds)))
            print "BA.clearFutureCallbacks: removing [%s]" % s
        if self.debug and len(self._bds) > 0:
            import pdb; pdb.set_trace()
        for bd in self._bds:
            if hasattr(bd, 'clear'):
                bd.clear()
            else:
                print "BA.clearFutureCallbacks: isn't it strange that I got a %r" % bd

    def _addBurstDeferred(self, bd):
        self._bds.append(bd)

    def __getattr__(self, k):
        actions_k = getattr(self._actions, k)
        if hasattr(actions_k, 'returnsbd'):
            return behaviorwrapbd(self, actions_k)
        return actions_k

    def __str__(self):
        return "<BA with %s waiting bds>" % (len(self._bds))
    
    __repr__ = __str__

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
        # We keep track of the registrations here to avoid multiples (TODO - this is the same as EventManager code)
        self._original_callbacks = {}
        self._original_events = dict([(event, set()) for event in self._eventmanager._events.keys()])
        self._calllaters = [] # TODO (small, Algorithmic) - this is currently suboptimal on clear. (O(N))
        self.verbose = True # TODO, options

    def clearFutureCallbacks(self):
        """ cancel callbacks, event registrations """
        for cb in self._calllaters:
            self._eventmanager.cancelCallLater(cb)
        for cb, event in self._registered:
            self._eventmanager.unregister(cb, event)
        if self.verbose and (len(self._calllaters) > 0 or len(self._registered) > 0):
            print "BEM.clearFutureCallbacks: removing CL [%s], E [%s]" % (
                ','.join(func_name(cb) for cb in self._calllaters),
                ','.join('%s->%s' % (event_name(e), func_name(cb)) for cb, e in self._registered))
        del self._calllaters[:]
        self._registered.clear()
        self._cb_to_wrapper.clear()

    def register(self, callback, event):
        if callback in self._callbacks and event in self._callbacks[event]:
            if self.verbose:
                print "WARNING: harmless reregister of callback"
                return
        # since we register using a lambda we must do the multiplicity checks here
        wrapper = lambda: self._behavior._applyIfNotStopped(callback, [], {})
        self._cb_to_wrapper[callback] = wrapper
        self._eventmanager.register(wrapper, event)
        self._registered.add((wrapper, event))
        if callback not in self._original_callbacks:
            self._original_callbacks[callback] = set()
        self._original_callbacks[callback].add(event)
        self._original_events[event].add(callback)

    def register_oneshot(self, callback, event):
        wrapper = lambda: self._behavior._applyIfNotStopped(callback, [], {})
        self._cb_to_wrapper[callback] = wrapper
        self._eventmanager.register_oneshot(wrapper, event)

    def unregister(self, callback, event=None):
        if callback in self._cb_to_wrapper:
            self._eventmanager.unregister(self._cb_to_wrapper[callback], event)
        if event is not None:
            self._original_callbacks[callback].discard(event)
            self._original_events[event].discard(callback)
        else:
            if callback in self._original_callbacks:
                events = self._original_callbacks[callback]
                del self._original_callbacks[callback]
                for event in events:
                    self._original_events[event].discard(callback)
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

class Behavior(Nameable):
    # No longer inherits from BurstDeferred - reimplementation with Deferred. no chains.

    _reset_count = 0

    def __init__(self, actions, name, *args, **kw):
        """  Note to inheriting folk: this constructor must be the /last/
        call in your constructor, since it calls your start method
        """
        self._resetDeferred()
        Nameable.__init__(self, name)
        self._actions = BehaviorActions(actions, self)
        self._world = actions._world
        self._eventmanager = BehaviorEventManager(actions._eventmanager, self)
        self._make = self._eventmanager.burst_deferred_maker.make
        self._succeed = self._eventmanager.burst_deferred_maker.succeed
        self._bd = None # if we are waiting on a single bd, this should be it. If we are waiting on more - split behavior?
        self.stopped = True

    def _resetDeferred(self):
        self._reset_count += 1
        self._d = Deferred()
        self.log("reset %s, %s" % (self._reset_count, id(self._d)))

    def get_stopped(self):
        return self._stopped
    def set_stopped(self, k):
        #print "Behavior %s: stopped = %s" % (self.name, k)
        self._stopped = k
    stopped = property(get_stopped, set_stopped)

    def _applyIfNotStopped(self, f, args, kw):
        if self.stopped:
            print "%s, %s: Who is calling me at this time? I am stopped" % (self, func_name(f))
            return
        return apply(f, args, kw)

    # BurstDeffered like behavior

    def toCondensedString(self):
        return deferredToCondensedString(self._d)

    def clear(self):
        self.log("WARNING: clear does nothing")
        #self._resetDeferred()

    def onDone(self, cb):
        chained = self._actions.make(self)
        def callAndCallBD(_, cb=cb, chained=chained):
            try:
                ret = cb()
            except TypeError, e:
                import pdb; pdb.set_trace()
            if not hasattr(ret, 'onDone'):
                return ret
            return ret.onDone(chained.callOnDone)
        self._d.addCallback(callAndCallBD).addErrback(log.err)
        return chained

    def callOnDone(self):
        """ same API as BurstDeferred, but doesn't actually call anyone if we are not
        stopped. Kind of strange. But meant to protect from anyone else calling it. Not sure
        if it even makes sense.
        """
        err = None
        if self.stopped:
            if self._d.called:
                # NOTE: I think this is a result of multiple callpaths ending in callLater - so
                # maybe I should make this an "official" tree and store the callers, and actually
                # make sure each calls once, AND if one calls, then the other, not even
                # report it as an error - since it won't be. Oh, how do you record the callers? Just
                # at runtime I guess (burst_util.getcaller could help)
                err = "callOnDone where _d is already called - ignored (seems harmless*)"
                #import pdb; pdb.set_trace()
            else:
                #print "Behavior: callOnDone ok"
                self._d.callback(None)
                self._d._frame = sys._getframe()
                # XXX tell the super to remove us from the parent? or have all BurstDeferreds
                # act like that? i.e. breaking parent-child when child has fired?
        else:
            err= "callOnDone being called while running - ignored. Probably IsRunningMoveCoordinator bug (see comment above)"
        if err:
            self.log("WARNING: %s" % err)

    def getDeferred(self):
        return self._d

    # Core Behavior API

    def stop(self):
        """ Stops the behavior, and returns a BD for stoppage complete. If already stopped,
        returns a succeedBD.

        Stopping also sets ourselves to complete, by calling callOnDone.
        """
        if self.stopped:
            if self._d.called:
                self.log("WARNING: self._d already called")
                return self._succeed(self)
            if len(self._d.callbacks) > 0:
                self.log("WARNING: calling stop when already stopped, with callbacks waiting: %s" %
                    self.toCondensedString())
            return self._succeed(self).onDone(self.callOnDone)
        if self._bd: # This is the customary bd for any action we are waiting on. TODO - stop using this, BehaviorActions makes it obsolete.
            self._bd.clear()
            self._bd = None
        self._eventmanager.clearFutureCallbacks()
        self._actions.clearFutureCallbacks()
        #self.log("Calling _stop")
        self.stopped = 'inprogress' # TODO kludge - we do need a tri-state, but that-is-not-the-way (using the fact that a non empty string is True)
        bd = self._stop()
        self.stopped = True # after self._stop we are really stopping, but better then before.
        assert(bd)
        # Hack to get out of a recursion right now:
        # if bd._ondone[0][0].im_self==self we will be calling ourselves.
        # even simpler, this happens only if bd is already done.
        if bd.completed():
            ret = self._actions.succeed(self).onDone(self.callOnDone)
        else:
            ret = bd.onDone(self.callOnDone)
        return ret

    def start(self, **kw):
        if not self.stopped: return self
        # DISCUSSION: (talking to yourself again? and storing distributed copies?!)
        # every Behavior is a BurstDeferred. That means users will onDone on it, and
        # getDeferred() from it. Whenever they call start() they expect this to be "renewed",
        # so basically we should do a clear here.. no?
        if len(self._d.callbacks) > 0:
            self.logverbose("Questionable: Removing some callbacks and setting completed to false")
            self.logverbose("              %s" % self)
        self._resetDeferred()
        self.stopped = False
        self._start(firstTime=True, **kw)
        return self

    def log(self, msg):
        print "%s: %s" % (self.__class__.__name__, msg)

    def logverbose(self, msg):
        if self.verbose:
            print "%s: %s" % (self.__class__.__name__, msg)

    #####  Override by Inheritance  #####

    def _start(self, firstTime=False, **kw):
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

    """ InitialBehavior's are what Player uses as the main_behavior object, they
    are the actualy "main" of our program, when all robocup rules / gamecontroller stuff
    is taken out of the way. """

    # TODO - should add player to constructor
    def __init__(self, actions, name, initial_pose=poses.INITIAL_POS):
        super(InitialBehavior, self).__init__(actions=actions, name=name)
        self._initial_pose = initial_pose

    # TODO - remove and put in constructor
    def setPlayer(self, player):
        self._player = player

