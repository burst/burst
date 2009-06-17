'''
Created on Jun 16, 2009

@author: Alon & Eran
'''

#from burst_util import (BurstDeferred, Nameable, calculate_middle, calculate_relative_pos, polar2cart, cart2polar, nicefloats)

# local imports
#import burst
from burst.behavior import ContinuousBehavior

class TargetFinder(ContinuousBehavior):
    ''' Continuous target finder & tracker '''

    def __init__(self, actions, targets, start = True):
        super(TargetFinder, self).__init__(actions=actions, name='%s Finder' % [
                                    target.name for target in targets])
        if len(targets) < 1:
            raise RuntimeException("Cannot find null set")
        self._targets = targets
        self._onTargetFoundCB = None
        self._onTargetLostCB = None
        self.verbose = False
        if start:
            self.start()

    def setOnTargetFoundCB(self, cb):
        self._onTargetFoundCB = cb

    def _callOnTargetFoundCB(self):
        if self._onTargetFoundCB:
            self._onTargetFoundCB()

    def setOnTargetLostCB(self, cb):
        self._onTargetLostCB = cb

    def _callOnTargetLostCB(self):
        if self._onTargetLostCB:
            self._onTargetLostCB()

    def getTargets(self):
        return self._targets

    def _start(self):
        print "TargetFinder looking for: %s" % (','.join(s.name for s in self._targets))
        # If a search has completed with our targets and they were found in this frame, go to tracking.
        # We give seen objects a priority over recently_seen objects
        seen_objects = [t for t in self._targets if t.seen]
        seen_objects.extend([t for t in self._targets if t.recently_seen and not t.seen])

        if len(seen_objects) > 0:
            # reset targets to the first seen object (could be arbitrary if we were just called)
            self._targets =  [seen_objects[0]]
            target = self._targets[0]
            print "will track %s" % target.name
            # NOTE: to make the behavior happy we need to always keep the deferred we are
            # waiting on at self._bd ; because Tracker doesn't provide any bd we create
            # one using self._actions._make
            self._bd = self._actions._make(self)
            self._bd.onDone(self._start)
            self._actions.track(target, lostCallback=self._bd.callOnDone)
            self._callOnTargetFoundCB()
        else:
            # none of our targets are currently seen, start a new search.
            print "targets not seen (%s), searching for it" % [t.name for t in self._targets]
            self._bd = self._actions.search(self._targets, center_on_targets=True, stop_on_first=True)
            self._bd.onDone(self._start)
            self._callOnTargetLostCB()

    def stop(self):
        super(TargetFinder, self).stop()
        self._actions.tracker.stop()
        self._actions.searcher.stop()
