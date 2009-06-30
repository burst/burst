from math import pi

import burst
import burst_events
from burst.behavior import Behavior
import burst_consts

############################################################################

# TODO - keep actions instead of searcher? who else would use
# these commands? too many "smart" ways to connect actions, makes it /harder/
# to concoct elequent 'just complex enough' behaviors

class HeadMovementCommand(object):
    def __init__(self, actions, headYaw, headPitch, interpTime=1.0):
        self._actions = actions
        self.headYaw = headYaw
        self.headPitch = headPitch
        self.interpTime = interpTime
    def __call__(self):
        return self._actions.moveHead(self.headYaw, self.headPitch, self.interpTime)

class ComplexAndBrokenCenteringCommand(object):
    """ Turn towards an initial position, then execute centering
    a few times, each time using the most centered position currently
    known to bootstrap."""
    def __init__(self, actions, headYaw, headPitch, target, repeats=2):
        """ repeats - number of times to run centering. First time the
        target is centered, or if repeats times pass, we call the bd returned
        """
        self._actions = actions
        self._yaw, self._pitch, self._target = headYaw, headPitch, target
        self._repeats = self._total_repeats = repeats
    def onCenteringDone(self):
        # TODO - Crude hack, to avoid CenteringCommand continuing when searcher is stopped.
        # real solution - turn this into a Behavior, have Searcher.stop stop the current
        # command.
        if self._actions.searcher.stopped: return
        # called both on centering and on target lost
        if self._target.centered_self.sighted_centered or self._repeats <= 0:
            self._bd.callOnDone()
            return
        print "CenteringCommand: starting trial %s out of %s" % (self._total_repeats - self._repeats + 1,
            self._total_repeats)
        self._repeats -= 1
        new_yaw, new_pitch = self._target.centered_self.estimated_yaw_and_pitch_to_center()
        self._actions.moveHead(new_yaw, new_pitch).onDone(
            lambda: self._actions.centerer.start(target=self._target).onDone(self.onCenteringDone)
        )
    def __call__(self):
        self._actions.moveHead(self._yaw, self._pitch).onDone(self.onCenteringDone)
        self._bd = self._actions.make(self)
        return self._bd

class CenteringCommand(object):
    """ move towards, then call the centerer """
    def __init__(self, actions, headYaw, headPitch, target):
        """ repeats - number of times to run centering. First time the
        target is centered, or if repeats times pass, we call the bd returned
        """
        self._actions = actions
        self._yaw, self._pitch, self._target = headYaw, headPitch, target
    def __call__(self):
        return self._actions.headTowards(self._target).onDone(
            lambda: self._actions.centerer.start(target=self._target))

class TurnCommand(object):
    def __init__(self, actions, thetadelta):
        self._actions = actions
        self.thetadelta = thetadelta
    def __call__(self):
        return self._actions.turn(self.thetadelta)

class SwitchCameraCommand(object):
    def __init__(self, actions, whichCamera):
        self.actions = actions
        self.whichCamera = whichCamera
    def __call__(self):
        return self.actions.setCamera(self.whichCamera)

class WaitCommand(object):
    def __init__(self, eventmanager, frames):
        if frames < 0:
            raise Exception("The number of frames to wait must be non-negative.") # TODO: Positive?
        self._eventmanager = eventmanager
        self._frames = frames
    def __call__(self):
        time_delta = self._frames * self._eventmanager.dt
        bd = self._eventmanager.burst_deferred_maker.make(self)
        self._eventmanager.callLater(time_delta, bd.callOnDone)
        return bd

def searchMovesIter(searcher):
    while True:
        for headCoordinates in [(0.0, -0.6), (0.0, 0.6), (1.0,  0.5), (-1.0, 0.5),
                                (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
            yield HeadMovementCommand(searcher._actions, *headCoordinates)
        # Give the robot time to see the ball before executing the costly turn command.
        yield WaitCommand(searcher._eventmanager, 3)
        yield TurnCommand(searcher._actions, -pi/2)

def searchMoveIterWithoutAnythingButHeadMovements(searcher):
    while True:
        for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (-1.0, 0.5),
                                (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
            yield HeadMovementCommand(searcher._actions, *headCoordinates)

def finiteSearchMoveIterWithoutAnythingButHeadMovements(searcher):
    for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (-1.0, 0.5),
                            (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
        yield HeadMovementCommand(searcher._actions, *headCoordinates)

def searchMovesIterWithCameraSwitching(searcher):
    while True:
        if not searcher._actions.currentCamera == burst_consts.CAMERA_WHICH_BOTTOM_CAMERA:
            yield SwitchCameraCommand(searcher._actions, burst_consts.CAMERA_WHICH_BOTTOM_CAMERA)
        for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0,  0.5), (-1.0, 0.5),
                                (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
            yield HeadMovementCommand(searcher._actions, *headCoordinates)
        yield SwitchCameraCommand(searcher._actions, burst_consts.CAMERA_WHICH_TOP_CAMERA)
        for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0,  0.5), (-1.0, 0.5),
                                (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
            yield HeadMovementCommand(searcher._actions, *headCoordinates)
        yield TurnCommand(searcher._actions, -pi/2)

def goalSearchIter(searcher):
    yield SwitchCameraCommand(searcher._actions, burst_consts.CAMERA_WHICH_TOP_CAMERA)
    #for t in searcher.targets:
    #    yield lambda: searcher._actions.headTowards(t)
    cur_yaw = searcher._actions._world.getAngle('HeadYaw')
    w =  1.0/3.0 # secs for pi turn
    print "GOAL SEARCH: Before All Turns"
    for turn in [pi/2, pi/2]:
        for headCoordinates in [(pi/2, 0.0, (pi/2-cur_yaw)/pi/w), (-pi/2, 0.0, 1.0/w)]:
            yield HeadMovementCommand(searcher._actions, *headCoordinates)
        # so we didn't find the targets - take the posts we find, turn the complement.
        #if set(searcher.seen_objects
        yield turn
        print "GOAL SEARCH: After Turn"
    for headCoordinates in [(pi/2, 0.0, (pi/2-cur_yaw)/pi/w), (-pi/2, 0.0, 1.0/w)]:
        yield HeadMovementCommand(searcher._actions, *headCoordinates)

def ballSearchIter(searcher):
    # Start by turning in place, then move. We cannot move randomly, except for being inefficient
    # it is also illegal to exit the field, so instead go to the more distant goal.
    yield SwitchCameraCommand(searcher._actions, burst_consts.CAMERA_WHICH_BOTTOM_CAMERA)
    for headCoordinates in [(0.0, -0.5), (0.0, 0.5), (1.0, 0.5), (-1.0, 0.5),
                            (-1.0, 0.0), (1.0, 0.0), (1.0, -0.5), (-1.0, -0.5)]:
        yield HeadMovementCommand(searcher._actions, *headCoordinates)

class SearchPlanner(object):
    """ The planner determines the next actions, but the searcher
    takes care of the seen events. There is a slight breaking in this
    pattern when we center on targets - then temporarily the tracker
    takes care of both actions and seen events """

    def __init__(self, searcher, center_on_targets=False, baseIter=searchMovesIter):
        self.verbose = burst.options.verbose_tracker
        self._searcher = searcher
        self._baseIter = baseIter(searcher)
        self._nextTargets = []
#            self._lastPosition = searcher.self. # TODO: return to the last position after a chain of targets.
        if center_on_targets:
            self._centerCommand = CenteringCommand
        else:
            self._centerCommand = (lambda actions, yaw, pitch, target:
                HeadMovementCommand(actions, yaw, pitch))

    def feedNext(self, target):
        self._nextTargets.append(target)

    def next(self):
        if len(self._nextTargets) == 0:
            self._report("giving a command according to the base-iterator.")
            return self._baseIter.next()
        else:
            target = self._nextTargets[0]
            del self._nextTargets[0]
            self._report("giving a centering command: %s" % target.name)
            yaw, pitch = target.centered_self.estimated_yaw_and_pitch_to_center()
            return self._centerCommand(self._searcher._actions, yaw, pitch, target)

    def hasMoreCenteringTargets(self):
        return self._nextTargets != []

    def _report(self, string):
        if self.verbose:
            print "Planner: %s" % string

    def wantedMove(self):
        return self._wantedMove

# Various other strategies for the searcher

def NoBodyMovesSearchPlanner(searcher, center_on_targets):
    """
    Finite
    Don't turn the body, just the head.
    """
    return SearchPlanner(searcher=searcher, center_on_targets=center_on_targets,
        baseIter=finiteSearchMoveIterWithoutAnythingButHeadMovements)

# Infinite
# Start with head turns, then turn the body
WithBodyMovesSearchPlanner=SearchPlanner

def TargetsAndLocalizationBasedSearchPlanner(searcher, center_on_targets):
    """
    Infinite
    Searches using knowledge of the relation between the targets (left and right posts)
    and based on availability of localization data
    """
    # Basic decision: return an iterator already suited for the targets
    targets = searcher.targets
    world = searcher._world
    for baseIter, predicate, msg in [
        (goalSearchIter, lambda targets: len(set(targets) & world.all_posts) > 0,
            "Looking for a Goal, using specific search iterator"),
        (ballSearchIter, lambda targets: set(targets) == set([world.ball]),
            "Looking for a Ball, using specific search iterator")
        ]:
        if predicate(targets):
            baseIter = baseIter
            break
    else:
        msg = "Not looking for a goal, nor for the ball - using general iterator"
        baseIter = finiteSearchMoveIterWithoutAnythingButHeadMovements
    print "Searcher: %s" % msg
    return SearchPlanner(searcher=searcher, center_on_targets=center_on_targets,
        baseIter=baseIter)

# TODO: Have the head turned the way we're turning. # Setting pi/2 to -pi/2 should have solved this, for now.
# TODO: Clear foot steps if found while turning.
# TODO: More efficient head movements (speed).
# TODO: More efficient head movements (order).
# TODO: Center while searching, so that you can move freely about.

############################################################################

class Searcher(Behavior):

    def __init__(self, actions):
        super(Searcher, self).__init__(actions=actions, name='Searcher')
        self.verbose = burst.options.verbose_tracker
        self._search_count = [0, 0] # starts, stops
        self._reset()
        # this is the default "did I see all targets" function, used
        # by searchHelper to provide both "all" and "one off" behavior.
        self._seenTargets = self._seenAll
        self._wantedMove = None

    def _reset(self):
        """ called when starting a new search """
        self._timeoutCallback = None
        self.seen_objects = []
        self._searchMoves = None
        #self._deferred = None
        self.targets = []
        self._report("Searcher: RESET")
        self._eventToCallbackMapping = {}
        self._wantedMove = None

    def _report(self, *strings):
        if self.verbose:
            self.log("%s: %s" % (self._search_count, '\n'.join(strings)))

    # Player / Behavior API

    def search_conditioned(self, targets, seenTargetsCB, center_on_targets=True, timeout=None, timeoutCallback=None,
            searchPlannerMaker=TargetsAndLocalizationBasedSearchPlanner):
        self._seenTargets = seenTargetsCB

    def search_one_of(self, targets, center_on_targets=True, timeout=None, timeoutCallback=None,
            searchPlannerMaker=TargetsAndLocalizationBasedSearchPlanner):
        self._seenTargets = self._seenOne
        return self.start(targets=targets, center_on_targets=center_on_targets, timeout=timeout,
            timeoutCallback=timeoutCallback, searchPlannerMaker=searchPlannerMaker)

    def search(self, targets, center_on_targets=True, timeout=None, timeoutCallback=None,
            searchPlannerMaker=TargetsAndLocalizationBasedSearchPlanner):
        self._seenTargets = self._seenAll
        return self.start(targets=targets, center_on_targets=center_on_targets,
            timeout=timeout, timeoutCallback=timeoutCallback,
            searchPlannerMaker=searchPlannerMaker)

    def wantsToMove(self):
        return self._wantedMove is not None

    def wantedMove(self):
        """ returns either a single float for heading, or a triple for (dx, dy, dh) """
        return self._wantedMove

    # Complementary setter for wanted move

    def _setWantedMove(self, move):
        self._wantedMove = move

    # Local Methods

    def _start(self, firstTime, targets, center_on_targets,
                timeout, timeoutCallback, searchPlannerMaker):
        '''
        Search fo the objects in /targets/.
        If /center_on_targets/ is True, center on those objects.
        If a /timeout/ is provided, quit the search after that many seconds.
        If a /timeoutCallback/ is provided, call that when and if a timeout occurs.
        '''
        self._reset()

        # Forget where you've previously seen these objects - you wouldn't be looking for them if they were still there.
        # TODO - history? (i.e. do keep these things, but with times - that would be perfect for
        # later applying a filter, i.e. kalman or particle or whatever. The localizer would keep track of those things).
        for target in targets:
            target.centered_self.clear()

        self.log("search started for %s %s, seenTargets = %s." % (','.join([
            '%s%s%s' % (t.name, ' sighted?! ' if t.centered_self.sighted else '',
                ' sighted_centered?! ' if t.centered_self.sighted_centered else '')
                    for t in targets]),
            'with centering' if center_on_targets else 'no centering',
            func_name(self._seenTargets)))

        self._search_count[0] += 1
        self.targets = targets[:]
        self._center_on_targets = center_on_targets
        self._timeoutCallback = timeoutCallback

        # Register for the timeout, if one has been asked for.
        if not timeout is None:
            self._eventmanager.callLater(timeout, self._onTimeout)

        # For each target you are searching for, have a callback lined up for the event of seeing it.
        for target in targets:
            event = target.in_frame_event
            callback = lambda obj=target, event=event: self._onSeen(obj, event)
            self._eventmanager.register(callback, event)
            self._eventToCallbackMapping[event] = callback

        # Launch the search, according to some search strategy. Do this after setting self.targets, so it can decide
        # based on the searched for targets.
        self._searchPlanner = searchPlannerMaker(self, center_on_targets)
        self._eventmanager.callLater(0, self._nextSearchMove) # The centered_selves have just been cleared. # TODO: Necessary.

        # shortcut if we already see some or all of the targets
        for target in self.targets:
            if target.seen:
                self._onSeen(target, target.in_frame_event) # TODO - recently_seen?

    def _onSeen(self, obj, event):
        self._report("Searcher: seeing %s" % obj.name)
#            print "\nSearcher seeing ball?: (ball seen %s, ball recently seen %s, dist: %3.3f, distSmoothed: %3.3f, ball bearing: %3.3f)" % (
#                self._world.ball.seen, self._world.ball.recently_seen, self._world.ball.dist, self._world.ball.distSmoothed, self._world.ball.bearing)

        #if len(self._eventToCallbackMapping) == 0: return
        if not obj in self.seen_objects:
            self._report("Searcher: first time seen %s" % obj.name)
            #self._eventmanager.unregister(self._onSeen, event)
            if event in self._eventToCallbackMapping:
                self._report("Searcher: unregistering %s (%s)" % (event, burst_events.event_name(event)))
                cb = self._eventToCallbackMapping[event]
                self._eventmanager.unregister(cb, event)
                del self._eventToCallbackMapping[event]
            self.seen_objects.append(obj)
            if self._center_on_targets:
                self._report("Next, I'll center on %s" % obj.name)
                self._searchPlanner.feedNext(obj)

    def _nextSearchMove(self):
        ''' Whenever a movement is finished, either the search is done, or a new movement should be issued. '''
        if not self.stopped:
            if not self._seenTargets(self.seen_objects) or self._searchPlanner.hasMoreCenteringTargets():
                try:
                    next_searcher_action = self._searchPlanner.next() # UGLY - this will call self.setWantedMove if it wants one
                except StopIteration:
                    self.log("Could not find any of the targets and no suggested movement")
                    self.stop() # TODO - say "failed"
                else:
                    # specific check for a movement command (which is not an action at all)
                    if not callable(next_searcher_action):
                        self._setWantedMove(next_searcher_action)
                        self.stop()
                    else:
                        next_searcher_action.__call__().onDone(self._nextSearchMove)
                        self._report("%s, %s" % (self.targets,
                            self._searchPlanner.hasMoreCenteringTargets() and 'has more centering targets' or 'done centering'))
            else:
                self.stop()

    def _seenOne(self, seen_objects):
        """ function for search_one_of, checks if one of the supplied targets
        has been seen """
        self._report("_seenOne: len(self.seen_objects) = %s" % len(self.seen_objects))
        return len(seen_objects) >= 1

    def _seenAll(self, seen_objects):
        """ default _seenTargets function, checks that all
        targets have been seen """
        for target in self.targets:
            if not target in seen_objects:
                self._report("_seenAll FALSE")
                return False
        self._report("_seenAll TRUE")
        return True

    def _stop(self):
        ''' Wrapping up once a search has been successfully completed. '''
        self.log("search completed for %s %s %s. Seen: %s" % (','.join([t.name for t in self.targets]),
            self._center_on_targets and 'with centering' or 'no centering',
            self._seenTargets == self._seenAll and 'for all' or 'for one',
            self.seen_objects))

        self._search_count[1] += 1
        self._actions.centerer.stop()
        return self._actions.getCurrentHeadBD() # XXX THIS IS BROKEN. Should be returning a specific BD - not the Head BD. That's like returning the general cause, instead of the specific cause.

    def _onTimeout(self):
        ''' The event for a searching having timed-out. '''
        if not self.stopped:
            timeoutCallback = self._timeoutCallback
            self.stop()
            if not timeoutCallback is None:
                timeoutCallback()

