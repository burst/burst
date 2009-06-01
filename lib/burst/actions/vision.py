from burst.events import *
import burst
from burst_util import BurstDeferred, Deferred

class Tracker(object):
    
    """ track objects by moving the head """
    
    def __init__(self, actions):
        self._target = None
        self._actions = actions
        self._eventmanager = actions._eventmanager
        self._stop = True
        self._on_lost = None
        self._lost_event = self._in_frame_event = None
    
    def stopped(self):
        return self._stop
    
    def track(self, target, on_lost_callback=None):
        # don't track objects that are not seen
        if not target.seen:
            return
        self._target = target
        self._stop = False
        if hasattr(target, 'lost_event'):
            self._lost_event = target.lost_event
            if on_lost_callback:
                self._on_lost = BurstDeferred(self)
                self._on_lost.onDone(on_lost_callback)
            self._eventmanager.register(self._lost_event, self.onLost)
        self._in_frame_event = target.in_frame_event
        self.trackingStep()
    
    def onLost(self):
        self._eventmanager.unregister(self._lost_event)
        self.stop()
        if self._on_lost:
            self._on_lost.callOnDone()
    
    def stop(self):
        self._stop = True
        if self._in_frame_event:
            self._eventmanager.unregister(self._in_frame_event)
    
    def trackingStep(self, need_to_register=True):
        if self._stop: return
        maybe_bd = self._actions.executeTracking(self._target)
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
        self.trackingStep(need_to_register=False)
    
    def continueTracking(self):
        if self._stop:
            return
        else:
            self.trackingStep()

class SearchResults(object):
    
    def __init__(self):
        self.elevation, self.distance, self.bearing = None, None, None
        self.sighted = False

class Searcher(object):
    
    """ search for a bunch of targets by moving the head (conflicts with Tracker) """
    
    def __init__(self, actions):
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._searchlevel = None
        self._targets = []
        self.results = {}
        self._stop = True
    
    def stopped(self):
        return self._stop
    
    def stop(self):
        for event in self._events:
            self._eventmanager.unregister(event)
        self._stop = True
    
    def search(self, targets):
        self._targets = targets
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
            # best case - we are done
            self.stop()
            self._bd.callOnDone()
        else:
            # TODO - middleground
            print "targets {%s} NOT seen, searching again..." % (','.join(obj._name for obj in self._targets))
            self._searchlevel = (self._searchlevel + 1) % burst.actions.LOOKAROUND_MAX
            self._actions.lookaround(self._searchlevel).onDone(self.onScanDone)

    def onSeen(self, target):
        if self._stop: return
        # TODO - if we saw everything then stop scan
        # TODO - if we saw something then track it, only then continue scan
        result = self.results[target]
        if hasattr(target, 'distSmoothed'):
            result.distSmoothed = self._world.ball.distSmoothed
        result.dist = target.dist # TODO - dist->distance
        result.bearing = target.bearing
        result.elevation = target.elevation
        result.head_yaw = self._world.getAngle('HeadYaw')
        result.head_pitch = self._world.getAngle('HeadPitch')
        result.sighted = True
        