'''
Created on Jun 16, 2009

@author: Alon & Eran
'''

#from burst_util import (BurstDeferred, Nameable, calculate_middle, calculate_relative_pos, polar2cart, cart2polar, nicefloats)

# local imports
#import burst
from burst.behavior import ContinuousBehavior
from burst_util import DeferredList
import burst_consts

# TODO: If several targets are found simultaneously, track either the earlier one in
# the list of targets, or the one that is closer.

class TargetFinder(ContinuousBehavior):
    ''' Continuous target finder & tracker. Success is finding a single target (out of
        possibly multiple candidates). '''

    def __init__(self, actions, targets, start = True):
        super(TargetFinder, self).__init__(actions=actions, name='%s Finder' % [
                                    target.name for target in targets])
        if len(targets) < 1:
            raise RuntimeException("Cannot find null set")
        self._targets = targets
        self._onTargetFoundCB = None
        self._onTargetLostCB = None
        self._onSearchFailedCB = None
        self.verbose = False
        if start:
            self.start()

    # Callback helpers
    def setOnSearchFailedCB(self, cb):
        self._onSearchFailedCB = cb

    def _callOnSearchFailedCB(self):
        if self._onSearchFailedCB:
            self._onSearchFailedCB()

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

    def _start(self, firstTime=False):
        self.log("_start: %s (first time: %s)" % (','.join(s.name for s in self._targets), firstTime))
        self._iterate(callOnLost=False)

    def _onSearchOver(self):
        # we are looking for a single target, so don't check for self._targets, just len()>0
        if len(self._actions.searcher.seen_objects) == 0:
            self.log("_onSearchOver: didn't see any target, so calling user callback")
            self._callOnSearchFailedCB()
            # If we lost the targets, don't restart - let the user do it.
        else:
            print "TargetFinder._onSearchOver: Searcher.seen_objects = %s" % (self._actions.searcher.seen_objects)
            searcher_seen = self._actions.searcher.seen_objects
            seen_objects = self.calc_current_seen_objects()
            if len(searcher_seen) > 0 and len(seen_objects) == 0:
                print "Inconsistency of TargetFinder with searcher - will do manual headTowards, giving searcher seen priority."
                self._selectOneTargetFromCandidates(searcher_seen)
                self._actions.headTowards(self._targets[0]).onDone(self._iterate)
            else:
                self._iterate()

    def calc_current_seen_objects(self):
        """ returns an array with the seen objects from self._targets, uses also
        seen_recently. Used by _iterate and _onSearchOver """
        seen_objects = [t for t in self._targets if t.seen]
        seen_objects.extend([t for t in self._targets if t.recently_seen and not t.seen])
        return seen_objects

    def _selectOneTargetFromCandidates(self, seen_objects):
        # TODO - check that this actually works. (i.e. when searching for both posts, returns the one closest to the current yaw)
        bearings = [abs(t.bearing) for t in seen_objects]
        self._targets = [seen_objects[bearings.index(min(bearings))]]

    def _iterate(self, callOnLost=True):
        """
            Called by/as:
                lostCallback of tracker (TODO - should call some helper like onSearchOver)
                self._onSearchOver when search is done

            If target_finder doesn't find target, it first calls OnTargetLostCB,
            and only then starts a search (otherwise we might get "Target Found" before getting the "Target Lost")
        """
        # If a search has completed with our targets and they were found in this frame, go to tracking.
        # We give seen objects a priority over recently_seen objects

        # use top camera for a goal post or posts, bottom for anything else (i.e. the ball)
        camera_bd = self._actions.setCamera({
            False:burst_consts.CAMERA_WHICH_BOTTOM_CAMERA,
            True:burst_consts.CAMERA_WHICH_TOP_CAMERA}[bool(self._world.all_posts & set(self._targets))])
        seen_objects = self.calc_current_seen_objects()
        print "TargetFinder._iterate: seen_objects = %s" % (seen_objects)

        if len(seen_objects) > 0:
            if len(seen_objects) > 1:
                #for t in seen_objects:
                #    print "name: %s bearing: %f" % (t.name, t.bearing)
                # if more than 1 object seen, select the one with minimal bearing
                # we also reset the _targets so we'll track the same target if target lost
                self._selectOneTargetFromCandidates(seen_objects)
            else:
                self._targets = [seen_objects[0]]

            target = self._targets[0]
            self.log("will track %s" % target.name)
            camera_bd.onDone(
                lambda: self._actions.track(target=target, lostCallback=self._iterate))
            self._callOnTargetFoundCB()
        else:
            # none of our targets are currently seen, start a new search.
            self.log("targets not seen (%s), searching for it" % [t.name for t in self._targets])
            if callOnLost:
                self._callOnTargetLostCB()
            self._actions.search(
                self._targets, center_on_targets=True, stop_on_first=True).onDone(
                self._onSearchOver)

    def _stop(self):
        """ stops the finder (and internal tracker/searcher).
        returns a burst deferred on the completion of the stop (based on a possible
        current head movement """
        self._actions.tracker.stop()
        self._actions.searcher.stop()
        return self._actions.getCurrentHeadBD()

