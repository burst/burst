'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import BurstDeferred, Nameable, succeedBurstDeferred
import burst.moves.poses as poses

class Behavior(BurstDeferred, Nameable):

    def __init__(self, actions, name):
        """  Note to inheriting folk: this constructor must be the /last/
        call in your constructor, since it calls your start method
        """
        BurstDeferred.__init__(self, self)
        Nameable.__init__(self, name)
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._make = self._eventmanager.burst_deferred_maker.make
        self._succeed = self._eventmanager.burst_deferred_maker.succeed
        self._bd = None # if we are waiting on a single bd, this should be it. If we are waiting on more - split behavior?
        self._stopped = True

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
        """ Behavior specific burstdeferred fired on stop completion """
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
