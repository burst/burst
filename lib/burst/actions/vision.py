from burst.events import *
import burst
from burst_util import (
    BurstDeferred, Deferred, chainDeferreds)

# This is used for stuff like Localization, where there is an error
# that is reduced by having a smaller error - otoh tracker will take longer
# (possibly)
TRACKER_DONE_MAX_PIXELS_FROM_CENTER = 5 # TODO - calibrate? there is an optimal number.

class Tracker(object):
    
    """ track objects by moving the head """
    
    verbose = True

    def __init__(self, actions):
        self._target = None
        self._actions = actions
        self._eventmanager = actions._eventmanager
        self._stop = True
        self._on_lost = None
        self._lost_event = None
        self._in_frame_event = None
        # if _centering_done != None then on centering it is called and tracking
        # is stopped
        self._centering_done = None
    
    def stopped(self):
        return self._stop

    def _start(self, target, on_lost_callback):
        self._target = target
        self._stop = False
        if hasattr(target, 'lost_event'):
            self._lost_event = target.lost_event
            if on_lost_callback:
                self._on_lost = BurstDeferred(self)
                self._on_lost.onDone(on_lost_callback)
            self._eventmanager.register(self._lost_event, self.onLost)

    ############################################################################

    def center(self, target):
        """
        Center on target, returns a BurstDeferred.
        """
        # TODO - what happens if the target is lost during the centerring,
        #  but it doesn't have an associated "lost" event? lost can
        # happen because of occlusion, and because of vision problems (which
        # can be minimized maybe).
        if not target.seen: # sanity check (also makes sure we get the
                            # lost event when it happens
            return
        self._start(target, self._centeringOnLost)
        self._centering_done = BurstDeferred(None)
        self._centeringStep()
        # TODO: check that this works correctly if on the first
        # centering step we are already centered (by calling center twice!)
        return self._centering_done

    def _centeringOnLost(self):
        print "Centering and Lost target? - target = %s" % self._target._name
        self.stop()
        # TODO - call callback on problem (lost ball, etc - higher up,
        # presumably the Player instance, should deal with this).

    def _centeringStep(self):
        if self._stop: return
        if not self._target.seen: # TODO - manually looking for lost event. should be event based, no?
            self.onLost()
        centered, maybe_bd = self._actions.executeTracking(self._target)
        if self.verbose:
            print "CenteringStep: centered = %s, maybe_bd %s" % (centered,
                not maybe_bd and 'is None' or 'is a deferred')
        if centered:
            self.stop()
            self._centering_done.callOnDone()
        elif maybe_bd:
            maybe_bd.onDone(self._centeringStep)
        else:
            print "HUGE TODO - centering isn't centered, but can't move, what todo?"

    ############################################################################

    def track(self, target, on_lost_callback=None):
        """ Continuous tracking: keep the target in sight.
        """
        # don't track objects that are not seen
        if not target.seen:
            # TODO we immediately call the on_lost_callback - might
            # not be wise - could lead to loops
            if on_lost_callback:
                on_lost_callback()
            return
        self._start(target, on_lost_callback)
        self._centering_done = None
        self._in_frame_event = target.in_frame_event
        self._trackingStep()
    
    def onLost(self):
        self._eventmanager.unregister(self._lost_event)
        self.stop()
        if self._on_lost:
            self._on_lost.callOnDone()
    
    def stop(self):
        # don't erase any deferreds here! stop is called
        # before issuing the callbacks, allowing deferred's callee to
        # correctly check that tracker is not operating.
        self._stop = True
        if self._in_frame_event:
            self._eventmanager.unregister(self._in_frame_event)
    
    def _trackingStep(self, need_to_register=True):
        # TODO - we check self._target.seen explicitly, not relying on the
        # self.stop() call in self.onLost (tied to the event_lost), because
        # this avoids the case where this callback is called before the event
        # lost one - how to solve this in a nicer manner?
        if self._stop or not self._target.seen: return
        centered, maybe_bd = self._actions.executeTracking(self._target)
        # Three possible states:
        if maybe_bd:
            # we initiated a new action - wait for it to complete
            self._eventmanager.unregister(self._in_frame_event)
            maybe_bd.onDone(self.continueTracking)
        else:
            # target is centered, just wait using the in_frame/on_lost events
            # or else a head motion is in progress - same as target_centered.
            if need_to_register:
                self._eventmanager.register(self._in_frame_event, self.onTargetInFrame)
    
    def onTargetInFrame(self):
        if self._stop: return
        self._trackingStep(need_to_register=False)
    
    def continueTracking(self):
        if self._stop:
            return
        else:
            self._trackingStep()

class SearchResults(object):
    
    def __init__(self):
        self.elevation, self.dist, self.bearing = None, None, None
        self.sighted = False

class Searcher(object):
    
    """ search for a bunch of targets by moving the head (conflicts with Tracker) """
    
    def __init__(self, actions):
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._searchlevel = None
        self._targets = []
        self._seen_order = [] # Keeps the actual order targets were seen.
        self._center_on_targets = True
        self._stop = True
        self.results = {}
    
    def stopped(self):
        return self._stop
    
    def stop(self):
        for event in self._events:
            self._eventmanager.unregister(event)
        self._stop = True
    
    def search(self, targets, center_on_targets = False):
        self._targets = targets
        self._center_on_targets = center_on_targets
        del self._seen_order[:]
        self._stop = False
        # TODO - complete this mapping, add opponent goal, my goal
        
        self.results.clear()
        for target in targets:
            self.results[target] = SearchResults()
        
        self._events = []
        for obj in targets:
            event = obj.in_frame_event 
            """ go to work """
            self._eventmanager.register(event, lambda obj=obj: self.onSeen(obj))
            self._events.append(event)
            
        # TODO: Fix YELLOW to use opponent goal
        self._searchlevel = burst.actions.LOOKAROUND_QUICK
        self._actions.lookaround(self._searchlevel).onDone(self.onScanDone)
        
        # create a burst deferred to be called when we found all targets
        self._bd = BurstDeferred(self)
        return self._bd

    def onScanDone(self):
        if self._stop: return
        
        # see which targets have been sighted
        if all([result.sighted for result in self.results.values()]):
            # best case - all done
            if self._center_on_targets:
                # center on every target by reverse order of seen
                chainDeferreds(
                    [lambda _: self._actions.tracker.center(target).getDeferred()
                        for target in reversed(self._seen_order)]
                ).onDone(self._onFinishedScanning)
            else:
                self._onFinishedScanning()
        else:
            # TODO - middleground
            print "targets {%s} NOT seen, searching again..." % (','.join(obj._name for obj in self._targets))
            self._searchlevel = (self._searchlevel + 1) % burst.actions.LOOKAROUND_MAX
            self._actions.lookaround(self._searchlevel).onDone(self.onScanDone)

    def _onFinishedScanning(self):
        self.stop()
        self._bd.callOnDone()

    def onSeen(self, target):
        if self._stop: return
        self._seen_order.append(target)
        # TODO OPTIMIZATION - when last target is seen, cut the search
        self._updateResults(target) # These are not the centered results.

    def _updateResults(self, target):
        # TODO - if we saw everything then stop scan
        # TODO - if we saw something then track it, only then continue scan
        result = self.results[target]
        if hasattr(target, 'distSmoothed'):
            result.distSmoothed = self._world.ball.distSmoothed
        # relative location from naoman
        result.dist = target.dist # TODO - dist->distance
        result.bearing = target.bearing
        result.elevation = target.elevation
        result.head_yaw = self._world.getAngle('HeadYaw')
        result.head_pitch = self._world.getAngle('HeadPitch')
        # vision vars from naoman
        result.height = target.height
        result.width = target.width
        result.centerX = target.centerX
        result.centerY = target.centerY
        result.x = target.x # upper left corner
        result.y = target.y #
        # flag the sighted flag
        result.sighted = True
        result.sighted_time = self._world.time
        
