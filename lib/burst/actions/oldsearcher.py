############################################################################
raise Exception("Don't Import Me")

class OldSearcher(object):

    """ Search for a bunch of targets by moving the head (conflicts with Tracker).
    optionally center on each object as a kludge to fix localization right now.

    The results are stored in the target.center of each target.
    """

    def __init__(self, actions):
        self._actions = actions
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._center_on_targets = True
        self._stop = True
        self._targets = []
        self._seen_order = [] # Keeps the actual order targets were seen.
        self._seen_set = set()
        self._events = []
        self._searchlevel = None
        self._timeoutCallback = None
        self.verbose = burst.options.verbose_tracker

    def stopped(self):
        return self._stop

    def stop(self):
        self._unregisterEvents()
        self._stop = True
        self._timeoutCallback = None

    def search(self, targets, center_on_targets=True, timeout=None, timeoutCallback=None):
        '''
        Search fo the objects in /targets/.
        If /center_on_targets/ is True, center on those objects.
        If a /timeout/ is provided, quit the search after that many seconds.
        If a /timeoutCallback/ is provided, call that when and if a timeout occurs.
        '''

        if not timeout is None:
            self._eventmanager.callLater(timeout, self._timeout)
            self._timeoutCallback = timeoutCallback

        if self.verbose:
            print "OldSearcher: Started search for %s" % (', '.join(t._name for t in targets))
        self._targets = targets
        self._center_on_targets = center_on_targets
        del self._seen_order[:]
        self._seen_set.clear()
        self._stop = False

        for target in targets:
            target.centered_self.clear()

        # register to in frame event for each target object
        for obj in targets:
            event = obj.in_frame_event
            callback = lambda obj=obj: self._onSeen(obj)
            self._eventmanager.register(callback, event)
            self._events.append((event, callback))

        # TODO: Fix YELLOW to use opponent goal
        self._searchlevel = burst.actions.LOOKAROUND_QUICK
        self._actions.lookaround(self._searchlevel).onDone(self._onScanDone)

        # create a burst deferred to be called when we found all targets
        self._bd = BurstDeferred(self)
        return self._bd

    def _unregisterEvents(self):
        # should be idempotent
        for event, callback in self._events:
            self._eventmanager.unregister(callback, event)
        self._eventmanager.cancelCallLater(self._timeout)
        del self._events[:]

    def _timeout(self):
        """ called using callLater if timeout requested """
        if not self.stopped():
            if not self._timeoutCallback is None:
                self._timeoutCallback()
            self.stop()

    def _onOneCentered(self):
        target = self._center_target
        if self.verbose:
            print "OldSearcher: Center: %s centering done (updated by standard calc_events)" % target._name
        self._centerOnNext()

    def _centerOnNext(self):
        # need to first go to a close place, use angles last seen
        # TODO - use median of last seen angles, would be much closer
        # to reality
        try:
            self._center_target = target = self._center_targets.next()
        except StopIteration:
            #import pdb; pdb.set_trace()
            if self.verbose:
                print "CenterOnNext: DONE"
            self._onFinishedScanning()
            return

        c_target = target.centered_self
        if self.verbose:
            print "OldSearcher: moving towards and centering on %s - (%1.2f, %1.2f)" % (
                target._name, c_target.head_yaw, c_target.head_pitch)
        # Actually that head_yaw / head_pitch is suboptimal. We have also centerX and
        # centerY, it is trivial to add them to get a better estimate for the center,
        # still calling center afterwards.
        a1 = c_target.head_yaw, c_target.head_pitch
        a2 = (a1[0] - PIX_TO_RAD_X * (c_target.centerX - IMAGE_CENTER_X),
              a1[1] + PIX_TO_RAD_Y * (c_target.centerY - IMAGE_CENTER_Y))
        #nodding = a1, a2, a1, a2
        #bd = self._actions.chainHeads(nodding)
        bd = self._actions.moveHead(*a2)
        # target.centered_self is updated every step, we just need to do the centering head move.
        return bd.onDone(lambda _, target=target: self._actions.tracker.center(target)
                ).onDone(self._onOneCentered)

    def _onScanDone(self):
        if self._stop: return
        
        # see which targets have been sighted
        seen = set(target for target in self._targets if target.centered_self.sighted)
        unseen = set(target for target in self._targets if not target.centered_self.sighted)
        if self.verbose:
            print "Seen = #%d, Targets = #%d" % (len(seen), len(self._targets))
        if len(seen) == len(self._targets):
            # best case - all done
            self._unregisterEvents()
            if self._center_on_targets:
                # center on every target by reverse order of seen
                # TODO - chainDeferred would have been nicer (a list
                # instead of a 'lisp list' to represent the future)
                # but there is a bug with my getDeferred in context of chainDeferreds
                self._center_targets = reversed(self._seen_order)
                self._centerOnNext()
            else:
                self._onFinishedScanning()
        else:
            bd = self._runSpecializedStrategy(seen, unseen)
            if bd:
                if self.verbose:
                    print "OldSearcher: using specialized strategy for (seen %r, unseen %r)" % (
                        [t._name for t in seen], [t._name for t in unseen])
            else:
                if self.verbose:
                    print "OldSearcher: targets {%s} NOT seen, searching again..." % (','.join(obj._name for obj in unseen))
                self._searchlevel = (self._searchlevel + 1) % burst.actions.LOOKAROUND_MAX
                bd = self._actions.lookaround(self._searchlevel)
            bd.onDone(self._onScanDone)

    def _runSpecializedStrategy(self, seen, unseen):
        """ place to register any interesting strategy concerning the
        matrix of 2^{#targets} x 2^{#targets}. Used right now for
        any case where we missed one post but saw it's twin

        return None if we don't have a special strategy.
        """
        # TODO - specialized strategies fail, then what? should go back to overall scan.
        world = self._world
        yellow_bot, yellow_top, blue_bot, blue_top = (
            world.yglp, world.ygrp, world.bgrp, world.bglp)
        R, L = consts.joint_limits['HeadYaw'][:2]
        pitch = self._world.getAngle('HeadPitch')
        for yaw, s, u in [( L, yellow_bot, yellow_top), ( R, yellow_top, yellow_bot),
                          ( R, blue_bot, blue_top), ( L, blue_top, blue_bot)]:
            if s in seen and u in unseen:
                return self._actions.moveHead(yaw, pitch)
        return None

    def _onFinishedScanning(self):
        if self.verbose:
            print "OldSearcher: DONE"
        self.stop()
        self._bd.callOnDone()

    def _onSeen(self, target):
        if self._stop: return
        if not target.seen or not target.dist:
            if self.verbose:
                print "OldSearcher: onSeen but target seen=%r and dist=%r" % (target.seen, target.dist)
            return
        # TODO OPTIMIZATION - when last target is seen, cut the search
        #  - stop current move
        #  - call _onScanDone to start centering.
        if target not in self._seen_set:
            if self.verbose:
                print "OldSearcher: First Sighting: %s, dist = %s, centered: %s" % (target._name, target.dist, target.centered_self)
            self._seen_order.append(target)
            self._seen_set.add(target)


