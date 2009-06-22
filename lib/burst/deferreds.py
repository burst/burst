"""
Holds the BurstDeferredMaker which helps keep track of all deferreds.

This is used for the simple task of stopping all future deferreds, but
is also possibly a debug aid.
"""

from burst_util import (BurstDeferred, succeedBurstDeferred,
    func_name)
import burst

class OncePerRound(BurstDeferred):
    """ this looks like a regular BurstDeferred, but it works a little differently:
    It will wait to be called by whatever (use the callOnDone to chain it to the
    end of any event / burstdeferred you want to), but only call the callbacks
    you chain to it if they are the first during the current round, where round
    means "a unique value for world.time".

    >>> once = OncePerRound(self)
    >>> self._eventmanager.register(once.callOnDone, EVENT_GAME_STATE_CHANGED)
    >>> (and also self.onConfigured might call once.callOnDone)
    ...
    >>> t = 0
    >>> EVENT_GAME_STATE_CHANGED fires
    >>> it calls ... (stopped documenting when I realised I don't actually need this right now)
    """

    def __init__(self, world, data):
        super(OncePerRound, self).__init__(data)
        self._world = world
        self._last_called_on = self._world.time - 1 # assumed strictly monotonic
        self._per_turn_cbs = []

    def onDone(self, cb):
        # give this to the regular list
        ret = super(OncePerRound, self).onDone(cb)
        # also store it for keeps
        self._per_turn_cbs.append(cb) # XXX - duplicates are warmly accepted
        return ret
    
    def callOnDone(self):
        ret = None
        if self._world.time > self._last_called_on:
            self._last_called_on = self._world.time
            ret = super(OncePerRound, self).callOnDone()
            # re-arm
            for cb in self._per_turn_cbs:
                super(OncePerRound, self).onDone(cb)
        return ret

class BurstDeferredMaker(object):

    def __init__(self):
        self.verbose = burst.options.verbose_deferreds
        self._bds = []
        # TODO - should I be deleting those things? I think it's pretty harmless.
        # unless it prevents some serious garbage collection from happening..

    def make(self, data):
        if self.verbose:
            print "BurstDeferredMaker: making with data=%s" % data
        bd = BurstDeferred(data)
        self._bds.append(bd)
        return bd
    
    def succeed(self, data):
        if self.verbose:
            print "BurstDeferredMaker: succeeding with data=%s" % data
        bd = succeedBurstDeferred(data)
        self._bds.append(bd)
        return bd

    def wrap(self, deferred, data):
        """ return a BD that is called on the deferred """
        bd = self.make(data)
        if deferred.called:
            bd._completed = True
        else:
            deferred.addCallback(lambda _: bd.callOnDone())
        return bd

    def clear(self):
        # we can't just erase them - no good. So we change all the callbacks to
        # harmless prints (the prints help debug anything that was accidentally
        # left behind)
        if self.verbose:
            print "BurstDeferredMaker: clearing"
        for bd in self._bds:
            bd._ondone = [((lambda _, cb=cb: self._printOnDone(cb)), chain_deferred)
                for cb, chain_deferred in bd._ondone]
    def _printOnDone(self, cb):
        print "BurstDeferredMaker: short circuit of %s" % func_name(cb)

# XXX Currently unused class
class BDHolder(object):
    """ strangely named, this is the current movement BD kept for
    cleanly stopping - returned to stopper who can then wait for
    calling of this bd. This bd is the current action if any, otherwise
    will be a successfull bd. (an already called bd)
    """
    def __init__(self, success):
        self.bd = success
    def set(self, bd):
        self.bd = bd
        return bd

