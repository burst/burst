'''
Created on Jun 14, 2009

@author: Alon & Eran
'''

from burst_util import BurstDeferred, Nameable

class Behavior(BurstDeferred, Nameable):
    
    def __init__(self, actions, name):
        """  Note to inheriting folk: this constructor must be the /last/
        call in your constructor, since it calls your start method
        """
        BurstDeferred.__init__(self, self)
        Nameable.__init__(self, name)
        self._actions = actions
        self._bd = None # if we are waiting on a single bd, this should be it. If we are waiting on more - split behavior?
        self._stopped = True

    def stop(self):
        """ Doesn't call any callbacks (by convention), so safe to call first when overriding """
        if self._stopped: return 
        if self._bd:
            self._bd.clear()
        self._stopped = True

    def stopped(self):
        return self._stopped

    def start(self):
        if not self._stopped: return
        self._stopped = False
        self._start()

    def _start(self):
        pass # defaults to empty behavior

class ContinuousBehavior(Behavior):
    
    def onDone(self, cb):
        raise RuntimeException("You cannot register an onDone callback on a continuous behavior.")
    