#
# Event Manager, and a main loop
#

import traceback
import sys
import os
from time import time
from heapq import heappush, heappop, heapify
import logging

from twisted.python import log

import burst
from burst_util import DeferredList, func_name, Profiler, succeed, import_class
import burst_util
import burst.actions
from burst.player import Player

from burst_events import (FIRST_EVENT_NUM, LAST_EVENT_NUM,
    EVENT_STEP, EVENT_TIME_EVENT, EVENT_WORLD_LOCATION_UPDATED, event_name)
from burst_consts import NAOQI_1_3_8, NAOQI_VERSION

import burst_consts

################################################################################
logger = logging.getLogger('eventmanager')
info = logger.info
################################################################################

# Event handling utilities and decorators

def singletime(event):
    """ Decorator that is meant to be used on a generator. The generator
    starts, inits and yields. The event is then registered.
    The event fires, the generator is called, returns. Then we
    unregister it.

    Note: specifically meant for methods of Player - we use self as
    first argument, and specifically use self._eventmanager.register
    and self._eventmanager.unregister methods.
    """
    def wrap(f):
        def wrapper(self, *args, **kw):
            gen = f(self, *args, **kw)
            gen.next() # let it init itself
            def onEvent():
                try:
                    gen.next()
                except StopIteration:
                    pass
                except Exception, e:
                    info( "CAUGHT EXCEPTION: %s" % e)
                self._eventmanager.unregister(event, onEvent)
                info( "singletime: unregistering from %s" % event)
            info( "singletime: registering to %s" % event)
            self._eventmanager.register(event, onEvent)
        return wrapper
    return wrap

# And now for something simpler - just store the event at a handy place
# inside the method that will be using it.
#
# I tried adding register and unregister methods, but for now I'm stumped
# by the fact that this wrapper is called during class construction, and
# so is handed functions and not methods, and so when I call register
# I give the function and not the wrapper method, so when it is finally
# called it complains that it thought it needs to give 0 arguments but
# the callee wants 1 (the self).
def eventhandler(event):
    """ Decorator that just ties in the event into the method it wraps, for
    usage see for example player.Player.registerDecoratedEventHandlers
    """
    def wrap(f):
        f.event = event
        return f
    return wrap



################################################################################

class SuperEvent(object):

    def __init__(self, eventmanager, events):
        self._events = events
        self._waiting = set(events)
        self._eventmanager = eventmanager

class AndEvent(SuperEvent):

    def __init__(self, eventmanager, events, cb):
        super(AndEvent, self).__init__(eventmanager, events, cb)
        self._cb = cb
        for event in events:
            eventmanager.register(lambda self=self, event=event: self.onEvent(event), event)

    def onEvent(self, event):
        self._waiting.remove(event)
        if len(self._waiting) == 0:
            # BROKEN
            for event in self.events:
                self._eventmanager.unregister(event)
            self._cb()

################################################################################

class SerialEvent(SuperEvent):

    def __init__(self, eventmanager, events, callbacks):
        super(SerialEvent, self).__init__(eventmanager, events)
        self._callbacks = callbacks
        self._i = 0
        eventmanager.register(self.onEvent, self._events[0])

    def onEvent(self, event):
        self._eventmanager.unregister(self._events[self._i])
        self._callbacks[self._i]()
        self._i += 1
        if len(self._events) == self._i:
            return
        self._eventmanager.register(self.onEvent, self._events[self._i])

################################################################################

class EventManager(object):
    """ Class to handle all event routing. Mainly we have:
    anything in burst_events can be called with EventManager.register

    due to lack of time time events are the same, so you only have one
    and no support right now for multiple requestors (do that in your code
    you lazy bum)
    """

    _break_on_next_deferred = False

    def __init__(self, mainloop, world):
        """ In charge of computing when certain events happen, keeping track
        of callbacks, and calling them.
        """
        # The _events maps from an event enum to a set of callbacks (so order
        # of callback is undefined)
        self.verbose = burst.options.verbose_eventmanager
        self.frame = 0 # number of steps.
        self.num_callbacks_to_report = 2
        self._clearEventsAndCallbacks()
        self._world = world
        self._mainloop = mainloop # for updateTimeStep
        self.burst_deferred_maker = self._world.burst_deferred_maker
        self._should_quit = False
        self._call_later = [] # heap of tuples: absolute_time, callback, args, kw

        self.dt = burst.options.dt # THA time step. defaults to 100ms, but we are trying other values.

        self.unregister_all()

    def _clearEventsAndCallbacks(self):
        self._events = dict([(event, set()) for event in
                xrange(FIRST_EVENT_NUM, LAST_EVENT_NUM)])
        self._callbacks = {} # dictionary from callback to events set it is registered to

    def get_num_registered(self):
        return sum(len(v) for k, v in self._callbacks.items())

    def get_num_registered_events(self):
        return sum(1 for k, v in self._events.items() if len(v) > 0)

    def get_num_registered_callbacks(self):
        return len(self._callbacks)

    def resetCallLaters(self): # TODO: This should probably be removed. Considered harmful.
        del self._call_later[:]

    # World / Actions API
    def updateTimeStep(self, dt):
        self.dt = dt
        self._mainloop.updateTimeStep(dt)

    # User (Player, Behavior - from within the loop)

    def callLater(self, dt, callback, *args, **kw):
        """ Will call given callback after an approximation of dt milliseconds,
        specifically:
        REAL_DT = int(dt/self.dt) (int == largest integer that is smaller then)
        """
        # TODO - cancel option? if required then the way is a real Event class
        abstime = self._world.time + max(self.dt, dt)
        heappush(self._call_later, (abstime, callback, args, kw))

    def callLaterBD(self, dt):
        """ returns a BurstDeferred which is called in dt seconds """
        bd = self.burst_deferred_maker.make(self)
        self.callLater(dt, bd.callOnDone)
        return bd

    def cancelCallLater(self, callback):
        """ removes all pending call laters to 'callback' - if there are multiple,
        all will be removed!

        TODO: this is not very optimal, and also isn't always what the user wants """
        while callback in self._call_later:
            self._call_later.remove(callback)

    def register(self, callback, event):
        """ set a callback on an event.
        """
        # add to _callbacks
        assert(callable(callback))
        if callback not in self._callbacks:
            self._callbacks[callback] = set()
        if event in self._callbacks[callback]:
            if burst.options.verbose_reregister:
                info( "WARNING: harmless re-register of %s to %s" % (func_name(callback), event_name(event)))
            return
        self._callbacks[callback].add(event)
        # add to _events
        self._events[event].add(callback)
        if self.verbose:
            info( "EventManager: #_events[%d] = %s" % (event, len(self._events[event])))

    def register_oneshot(self, callback, event):
        def on_one_event():
            if self.verbose:
                info( "EventManager: one shot removal, before: %s, %s" % (
                            len(self._events[event]), self._events[event]))
            self.unregister(on_one_event, event)
            if self.verbose:
                info( "EventManager: one shot removal, after: %s, %s" % (
                            len(self._events[event]), self._events[event]))
            callback()
        on_one_event.func_name = 'on_one_event__%s' % (func_name(callback))
        self.register(on_one_event, event)

    def registerOneShotBD(self, event):
        bd = self.burst_deferred_maker.make(self)
        self.register_oneshot(bd.callOnDone, event)
        return bd

    def firstEventDeferred(self, *events):
        return DeferredList([self.registerOneShotBD(event).getDeferred() for event in events]
                            ,fireOnOneCallback=True)

    def unregister(self, callback, event=None):
        """Unregister the callback function callback, if event is given then from that
        event only, otherwise from all events it is registered for. If it isn't registered
        to anything then nothing will happen.
        """
        if self.verbose:
            info( "EventManager: unregister %s" % callback)
        if callback in self._callbacks:
            # remove from _events
            for event in self._callbacks[callback]:
                self._events[event].remove(callback)
            # remove from _callbacks
            del self._callbacks[callback]
        assert(callback not in self._callbacks)

    def unregister_all(self):
        for k in self._events.keys():
            self._events[k] = set()

    def quit(self):
        print "EventManager.quit called"
        self._should_quit = True

    def _removeAllPendingCallbacks(self):
        """ should only be called on quit (hence the underscore) by
        the BaseMainLoop.
        """
        self._clearEventsAndCallbacks()
        self.burst_deferred_maker.clear()

    def computePendingCallbacks(self):
        """ mainly split off from handlePendingCallbacks to allow easier debugging,
        by printing each frame's callbacks """
        self.frame += 1
        self._pending_events, deferreds = self._world.getEventsAndDeferreds()
        self._pending_deferreds = list(deferreds) # make copy, avoid endless loop

        # call later part 1 - find out which are called this round.
        self._current_call_later = current_call_later = self._call_later
        self._call_later = [] # new heap for anything created by the callbacks themselves,
                              # avoid endless loops.
        self._pending_call_laters = call_laters_this_frame = []
        while len(current_call_later) > 0:
            next_time = current_call_later[0][0]
            if self.verbose:
                info( "EventManager: we have some callLaters")
            if next_time <= self._world.time:
                next_time, cb, args, kw = heappop(current_call_later)
                call_laters_this_frame.append((cb, args, kw))
            else:
                break # VERY IMPORTANT..

        self._pending_event_callbacks = [(event, list(self._events[event])) for event in self._pending_events if len(self._events[event]) > 0]

        # Warn user on the tricky cases - when more then one cb happens
        # in a single frame
        self._num_deferreds = len(self._pending_deferreds)
        self._num_events = sum(len(cbs) for event, cbs in self._pending_event_callbacks)
        self._num_time_step = len(self._events[EVENT_STEP])
        self._num_call_laters = len(call_laters_this_frame)
        self._num_cbs_in_round = self._num_deferreds + self._num_events + self._num_time_step + self._num_call_laters
        if self.verbose and self._num_cbs_in_round >= self.num_callbacks_to_report:
            info( 'EventManager: you have %s = %s D + %s E + %s S + %s L cbs' % self.getPendingBreakdown())

    def getPendingBreakdown(self):
        return (self._num_cbs_in_round, self._num_deferreds, self._num_events, self._num_time_step,
                self._num_call_laters)

    def numberPendingCallbacks(self):
        return self._num_cbs_in_round

    def numberImportantPendingCallbacks(self):
        # TODO - Important? goes along with Intelligent and Object as good names
        if self._num_cbs_in_round > 0 and self._num_events > 0:
            #import pdb; pdb.set_trace()
            pass # TODO
        return self._num_cbs_in_round

    def handlePendingCallbacks(self):
        """ Call all callbacks registered based on the new events
        stored in self._world, call all callLaters, and call all fired deffereds.

        We use a delegation scheme, where the eventloop just asks the world for
        the actual events and deferreds that fired, and calls them itself, adding
        the callLaters and EVENT_STEP which it handles itself.

        Special care is taken so the following holds:
         * Any cb that by running disables further cb's is effective immediately -
           i.e. also during the rest of the current frame.
         * Any cb that by running enables a new cb is only effective from the next
           frame. This avoids possible recursion.
        """
        events = self._pending_events
        deferreds = self._pending_deferreds
        call_laters_this_frame = self._pending_call_laters
        # Code handling this "removal in cb" is noted as "handle possible removal"
        # to make the code more readable.

        # TODO - rename deferreds to burstdeferreds
        # Handle regular events - we keep a copy of the current
        # cb's for all events to make sure there is no loop.
        loop_event_cb = self._pending_event_callbacks
        for event, cbs in loop_event_cb:
            for cb in cbs:
                if cb in self._events[event]:  # handle possible removal
                    if self.verbose:
                        info("----------------EventManager-Events-----------")
                    cb()
                elif self.verbose:
                    info( "EventManager: %s removed by prior during step" % cb)
        # EVENT_STEP registrators are always called (again, list used to create a temp copy)
        for cb in list(self._events[EVENT_STEP]):
            if cb in self._events[EVENT_STEP]: # handle possible removal
                if self.verbose:
                    info("----------------EventManager-EventStep--------")
                cb()
            elif self.verbose:
                info( "EventManager: %s removed by prior during step" % cb)

        # Handle call later's (we counted before, now we run and merge)
        for cb, args, kw in call_laters_this_frame:
            if self.verbose:
                #info( "EventManager: calling callLater callback")
                info("----------------EventManager-CallLater--------")
            cb(*args, **kw)

        # now merge the new with the old
        if len(self._call_later) > 0:
            if self.verbose:
                info( "EventManager: callLater-cbs added callLaters! merging")
            self._call_later = self._current_call_later + self._call_later
            heapify(self._call_later) # TODO - implement merge, this is faster.
        else:
            self._call_later = self._current_call_later

        # Handle deferreds
        for deferred in deferreds:
            if burst.options.debug:
                d = deferred._data
                if hasattr(d, '__len__') and len(d) == 2:
                    print "EventManager: handle*: deferred._data = %s" % (str(d))
            if self._break_on_next_deferred:
                self._break_on_next_deferred = False
                import pdb; pdb.set_trace()
            if self.verbose:
                info("----------------EventManager-Deferreds--------")
            deferred.callOnDone()

    def _D_breakOnNextDeferred(self):
        self._break_on_next_deferred = True

    def debug_methods(self):
        print '\n'.join([x for x in dir(self) if x[:3] == '_D_'])

################################################################################

class BasicMainLoop(object):

    __running_instance = None

    def __init__(self, main_behavior_class=None):
        self._main_behavior_class = main_behavior_class
        self._ctrl_c_cb = None
        self._actions = None
        if self.__running_instance:
            raise SystemExit('BURST Event Loop constructed twice')
        self.__running_instance = self

        self._world = None
        self._actions = None
        self._eventmanager = None
        self._player = None

        # flags for external use
        self.finished = False       # True when quit has been called
        self._on_normal_quit_called = False

        self._profiler = None

        # debug flags
        self._ticker = burst.options.ticker or burst.options.trace_proxies

    # EventManager API (only one function)
    def updateTimeStep(self, dt):
        """ here to allow loops that don't just use eventmanager.dt to update themselves,
        i.e. twisted, pynaoqi """
        pass

    def _getNumberOutgoingMessages(self):
        return 0 # implemented just in twisted for now

    def _getNumberIncomingMessages(self):
        return 0

    def initMainObjectsAndPlayer(self):
        """ Must be called after burst.init() - so that any proxies can be
        created at will.
        """
        import actions
        import world

        if self._world is not None: return # prevent reinitialization

        # main objects: world, eventmanager, actions and player
        self._world = world.World()
        self._eventmanager = EventManager(mainloop = self, world = self._world)
        self._actions = actions.Actions(eventmanager = self._eventmanager)
        self._world._setActions(self._actions) # they shall never part now (nor be garbage collected. ti's ok)
        if self._main_behavior_class is None:
            jersey = self._world.robot.jersey
            self._main_behavior_class = import_class(burst_consts.JERSEY_NUMBER_TO_INITIAL_BEHAVIOR_MODULE_CLASS[jersey])
            info('Jersey %d, Behavior %s' % (jersey, self._main_behavior_class.__name__))
        self._player = Player(actions = self._actions, main_behavior_class=self._main_behavior_class)

    def cleanup(self):
        """ Should not do anything that does work on the robot (nothing
        that would return a deferred), just other cleanup: close files,
        print any needed debug info, etc.
        """
        self.finished = True # set here so an exception later doesn't change it
        self._world.cleanup()

    def onNormalQuit(self, naoqi_ok):
        """
        Start the quitting process -
            call Player.onStop
            remove all pending callbacks when that is done.

        return deferred for caller (SimpleMainLoop, TwistedMainLoop) to wait
        on if required, or None if nothing to wait on (maybe just replace with succeed - TODO
        """
        if self._on_normal_quit_called:
            info( "HARMLESS ERROR: second BaseMainLoop.onNormalQuit called")
            return
        self._on_normal_quit_called = True
        self._on_normal_quit__naoqi_ok = naoqi_ok
        stop_deferred = None
        if self._player:
            stop_deferred = self._player.onStop()

        # From this point onwards illegal moves (i.e. anything) are allowed.
        info( "MainLoop: ILLEGAL ROBOCUP moves ALLOWED from now on")
        burst.actions._use_legal = False

        if stop_deferred:
            return stop_deferred.onDone(self._onNormalQuit_playerStopDone).getDeferred()
        else:
            return self._onNormalQuit_playerStopDone()

    def _onNormalQuit_playerStopDone(self):
        naoqi_ok = self._on_normal_quit__naoqi_ok
        self._eventmanager._removeAllPendingCallbacks()
        d = succeed(None)
        if self._actions:
            if burst.options.passive_ctrl_c:# or not self._world.connected_to_nao:
                info( "BasicMainLoop: exiting")
            else:
                if naoqi_ok:
                    info( "BasicMainLoop: sitting, removing stiffness and quitting.")
                    d = self._actions.sitPoseAndRelax_returnDeferred()
            self._world._gameController.shutdown() # in parallel to sitting
        self.__running_instance = None
        return d

    def setCtrlCCallback(self, ctrl_c_cb):
        self._ctrl_c_cb = ctrl_c_cb

    def onCtrlCPressed(self):
        """ Returns None or the result of the callback, which may be a deferred.
        In that case shutdown will wait for that deferred
        """
        self._eventmanager._should_quit = True
        if self._ctrl_c_cb:
            return self._ctrl_c_cb(eventmanager=self._eventmanager, actions=self._actions,
                world=self._world)

    def _startBanner(self, s):
        print "="*80
        print "= %s =" % ((self._eventmanager._should_quit and 'quitting - event loop restarted' or s).center(76))
        print "="*80

    def _printTraceTickerHeader(self):
        print "="*burst_consts.CONSOLE_LINE_LENGTH
        print "Time Objs-CL|IN|PO|Right        |Left         |Ball         |Out|Inc|".ljust(burst_consts.CONSOLE_LINE_LENGTH, '-')
        print "="*burst_consts.CONSOLE_LINE_LENGTH

    def _printTraceTicker(self):
        """ debugging helper. prints a one line (up to overflow) state. """
        world_location_updated = (EVENT_WORLD_LOCATION_UPDATED in self._eventmanager._pending_events and 'p' or ' ')
        ball = self._world.ball.seen and 'B' or ' '
        opposing_lp = self._world.opposing_lp.seen and 'L' or ' '
        opposing_rp = self._world.opposing_rp.seen and 'R' or ' '
        unknown_opposing = self._world.opposing_goal.unknown.seen and 'U' or ' '
        our_lp = self._world.our_lp.seen and 'l' or ' '
        our_rp = self._world.our_rp.seen and 'r' or ' '
        unknown_our = self._world.our_goal.unknown.seen and 'u' or ' '
        targets = self._actions.searcher.targets
        def getjoints(obj):
            if obj not in targets: return False
            r = obj.centered_self
            if not r.sighted: return '             '
            return ('%0.2f %0.2f %s' % (r.head_yaw, r.head_pitch, r.sighted_centered and 'T' or 'F')).rjust(11)
        left_joints = getjoints(self._world.opposing_lp) or getjoints(self._world.our_lp) or '-------------'
        right_joints = getjoints(self._world.opposing_rp) or getjoints(self._world.our_rp) or '-------------'
        ball_joints = getjoints(self._world.ball)
        num_out = self._getNumberOutgoingMessages()
        num_in = self._getNumberIncomingMessages()
        total, deferreds, event_cbs, step_cbs, calllater_cbs = self._eventmanager.getPendingBreakdown()
        # LINE_UP is to line up with the LogCalls object.
        LINE_UP = 62
        print ("%4.1f %s%s%s%s%s%s%s%s-%02d|%02d|%02d|%s|%s|%s|%3d|%3d|%s D %s E %s S %s L|%s" % (
            self.cur_time - self.main_start_time,
            world_location_updated, ball,
            opposing_lp, opposing_rp, unknown_opposing,
            our_lp, our_rp, unknown_our,
            len(self._eventmanager._call_later),
            len(self._world._movecoordinator._initiated),
            len(self._world._movecoordinator._posted),
            left_joints, right_joints, ball_joints,
            num_out, num_out - num_in,
            deferreds, event_cbs, step_cbs, calllater_cbs,
            self.getCondensedState(),
            )).ljust(burst_consts.CONSOLE_LINE_LENGTH, '-')

    def getCondensedState(self):
        """ get a represnetation of the current "state". This is deemed to be the sum
        of all current possible callbacks, probably after some filtering. Condensed means
        less bytes, suitable for the ticker """
        em = self._eventmanager
        dont_print = set(['_announceSeeingYellowGoal', '_announceSeeingBlueGoal', '_announceNotSeeingBall', '_announceSeeingBall'])
        try:
            s = ','.join([x for x in map(func_name, [cb for cb, args, kw in em._pending_call_laters] +
                sum((list(cbs) for event, cbs in em._pending_event_callbacks), []) +
                list(em._events[EVENT_STEP])) +
                [x.toCondensedString() for x in em._pending_deferreds if x._ondone]
                if x not in dont_print]
                )
        except:
            print "ERROR, PDB-ing: BasicMainLoop.getCondensedState"
            import pdb; pdb.set_trace()
        return s

    def preMainLoopInit(self):
        """ call once before the main loop """
        self.main_start_time = time()
        self.cur_time = self.main_start_time
        self.next_loop = self.cur_time
        if self._ticker:
            self._printTraceTickerHeader()
        # First do a single world update - get values for all variables, etc.
        self.doSingleStep()
        # Second, set stiffness, move to initial position, and queue player entrace.
        def setLegalAndCallPlayerOnStart():
            burst.actions._use_legal = True
            info( "MainLoop: only LEGAL ROBOCUP moves allowed from now on")
            self._player.onStart()
        if NAOQI_VERSION == NAOQI_1_3_8: # Workaround for camera switch bug. TODO - location?
            top = self._actions.switchToTopCamera
            bottom = self._actions.switchToBottomCamera
            for what, dt in sum([[(top, b), (top, b+0.05), (top, b+0.1), (bottom, b+0.2), (bottom, b+0.25), (bottom, b+0.3)] for b in (0.0, 0.5)], []):
                self._eventmanager.callLater(dt, what)
        # Camera Switch to Bottom:
        #  can do this without waiting (better to set a barrier - i.e. deferredList)
        self._actions.switchToBottomCamera()
        self._actions._initPoseAndStiffness(self._player._main_behavior._initial_pose).onDone(setLegalAndCallPlayerOnStart)

    def doSingleStep(self):
        """ call once for every loop iteration
        TODO: This is just using a polling loop to emulate real
        event generation, once twisted is really used this should
        become mute, and twisted will call the eventmanager directly.
        eventmanager will then probably register directly with twisted.

        returns the amount of time to sleep in seconds
        """
        self._eventmanager.computePendingCallbacks()
        # Print ticker after computing all callbacks/events, but before executing them
        if burst.options.trace_proxies or (self._ticker and self._eventmanager.numberImportantPendingCallbacks() > 0):
            self._printTraceTicker()

        # reverse the order? arg.
        if burst.options.profile_player:
            self._profiler.runcall(self._eventmanager.handlePendingCallbacks)
        else:
            self._eventmanager.handlePendingCallbacks()
        self._world.collectNewUpdates(self.cur_time)
        self.next_loop += self._eventmanager.dt
        self.cur_time = time()
        if self.cur_time > self.next_loop:
#            info( "WARNING: loop took %0.3f ms" % ()
#                (self.cur_time - self.next_loop + self.dt
#                ) * 1000)
#            self.next_loop = self.cur_time
            return None
        else:
            return self.next_loop - self.cur_time

    def profile_filename(self):
        """ return name of file to keep profile results in, with extension """
        raise NotImplementedError("profile_filename")

    def profile_player_filename(self):
        raise NotImplementedError('profile_player_filename')

    def run(self):
        if burst.options.profile:
            self._profiler = Profiler(self.profile_filename())
            self._profiler.runcall(self._run_loop)
        else:
            if burst.options.profile_player:
                self._profiler = Profiler(self.profile_player_filename())
            self._run_loop()
        if self._profiler:
            self._profiler.close()

    def cleanupAfterNaoqi(self, _=None):
        """  cleanup, mainly close all threads (like movement threads)
        second arg for addCallback usage"""
        self._world._movecoordinator.shutdown() # close movement threads


################################################################################

class SimpleMainLoop(BasicMainLoop):

    """ Until twisted is installed on the robot this is the default event loop.
    It basically sleeps and polls. Some intelligence goes into not polling (sending
    socket requests) too much, that happens in World.update.
    """

    def __init__(self, main_behavior_class=None):
        super(SimpleMainLoop, self).__init__(main_behavior_class = main_behavior_class)
        self._keep_the_loop = True

        # need to call burst.init first
        burst.init()

        self.initMainObjectsAndPlayer()

    def profile_filename(self):
        return '%s.kcachegrind' % sys.argv[0].rsplit('.',1)[0]

    def profile_player_filename(self):
        return '%s_player.kcachegrind' % sys.argv[0].rsplit('.',1)[0]

    def _step_while_handling_exceptions(self):
        """ returns (naoqi_ok, sleep_time)
        A normal quit is either: Ctrl-C or eventmanager.quit()
        so only non normal quit is a caught exception (uncaught and
        you wouldn't be here)"""
        naoqi_ok, sleep_time = True, None
        if burst.options.catch_player_exceptions:
            try:
                naoqi_ok, sleep_time = (
                    self._step_while_handling_non_player_exceptions())
            except RuntimeError, e:
                if 'SOAP error:Connection refused' in str(e):
                    info( "naoqi quit, quitting")
                    import sys
                    sys.exit(-1)
            except Exception, e:
                info( "BasicMainLoop: caught player exception: %s" % e)
                import traceback
                import sys
                traceback.print_tb(sys.exc_info()[2])
        else:
            naoqi_ok, sleep_time = self._step_while_handling_non_player_exceptions()
        return naoqi_ok, sleep_time

    def _step_while_handling_non_player_exceptions(self):
        naoqi_ok, sleep_time = True, None
        try:
            sleep_time = self.doSingleStep()
        except RuntimeError, e:
            info( "BasicMainLoop: naoqi exception caught: %s" % e)
            info( "BasicMainLoop: quitting")
            naoqi_ok = False
            if 'SOAP:Connection refused' in str(e):
                info( "Naoqi quit (SOAP:Connection refused), exiting.")
                self.cleanupAfterNaoqi()
                import sys
                sys.exit(-1)
            raise

        return naoqi_ok, sleep_time

    def _run_loop(self):
        # actually start the loop twice:
        # once for real
        # second time for wrapup if ctrl-c caught

        ctrl_c_pressed = False
        self.preMainLoopInit() # Start point for Player / GameController

        try:
            self._run_loop_helper()
        except KeyboardInterrupt:
            info( "BasicMainLoop: ctrl-c detected.")
            ctrl_c_pressed = True
        # No ctrl-c here I hope
        if ctrl_c_pressed:
            try:
                self.onCtrlCPressed()
                self._run_loop_helper() # continue the loop, wait for pending moves etc.
            except KeyboardInterrupt:
                info( "BasicMainLoop: ctrl-c detected a second time. unclean exit.")
                raise SystemExit

    def _run_loop_helper(self):
        import burst
        self._startBanner("running custom event loop with sleep time of %s milliseconds" % (self._eventmanager.dt*1000))
        from time import sleep, time
        quitting = False
        # we need the eventmanager until the total end, to sit down and stuff,
        # so we actually quit on a callback, namely self._exitApp (hence the
        # seemingly endless loop)
        while self._keep_the_loop:
            naoqi_ok, sleep_time = self._step_while_handling_exceptions()
            # if quitting, start quitting sequence (sit down, remove stiffness)
            if self._eventmanager._should_quit and not quitting:
                quitting = True
                self.cleanup() # TODO - merge with onNormalQuit? what's the difference?
                d = self.onNormalQuit(naoqi_ok)
                if d:
                    d.addCallback(self.cleanupAfterNaoqi).addCallback(self._exitApp).addErrback(log.err)
            if sleep_time:
                sleep(sleep_time)

    def _exitApp(self, _):
        self._keep_the_loop = False

################################################################################

class TwistedMainLoop(BasicMainLoop):

    def __init__(self, main_behavior_class=None, reactor=True, startRightNow=True):
        super(TwistedMainLoop, self).__init__(main_behavior_class = main_behavior_class)
        self._do_cleanup = True
        self._reactor = reactor
        if reactor:
            self._install_sigint_handler(reactor)
        import pynaoqi
        self.con = pynaoqi.getDefaultConnection()
        self.started = False        # True when setStartCallback has been called
        self.quitting = False
        if startRightNow:
            self.start()

    def _install_sigint_handler(self, reactor):
        print "installing SIG_INT handler"
        orig_sigInt = reactor.sigInt
        self._ctrl_c_presses = 0
        def my_int_handler(reactor, *args):
            self._ctrl_c_presses += 1
            info( "TwistedMainLoop: SIGBREAK caught")
            if self._ctrl_c_presses == 1:
                if self.quitting:
                    info( "TwistedMainLoop: SIGBREAK: quitting already in progress")
                else:
                    self._startShutdown(naoqi_ok=True, ctrl_c_pressed=True)
            else:
                info( "Two ctrl-c - shutting down uncleanly")
                orig_sigInt(*args)

        reactor.sigInt = my_int_handler

    def profile_filename(self):
        return '%s_twisted.kcachegrind' % sys.argv[0].rsplit('.',1)[0]

    def profile_player_filename(self):
        return '%s_twisted_player.kcachegrind' % sys.argv[0].rsplit('.',1)[0]

    def start(self):
        self.con.modulesDeferred.addCallback(self._twistedStart).addErrback(log.err)
        self.started = True

    def _getNumberOutgoingMessages(self):
        return self.con.connection_manager._sent

    def _getNumberIncomingMessages(self):
        return self.con.connection_manager._returned

    def _twistedStart(self, _):
        info( "TwistedMainLoop: _twistedStart")
        self.initMainObjectsAndPlayer()
        info( "TwistedMainLoop: created main objects")
        from twisted.internet import task
        self.preMainLoopInit()
        self._startBanner("running TWISTED event loop with sleep time of %s milliseconds" % (self._eventmanager.dt*1000))
        self._main_task = task.LoopingCall(self.onTimeStep)
        self._main_task.start(self._eventmanager.dt)

    def updateTimeStep(self, dt):
        """ here to allow loops that don't just use eventmanager.dt to update themselves,
        i.e. twisted, pynaoqi """
        self._main_task.interval = dt

    def _run_loop(self):
        if not self._reactor:
            info( "TwistedMainLoop: not in control of reactor")
            return
        self._reactor.run() #installSignalHandlers=0)
        info( "TwistedMainLoop: event loop done")

    def shutdown(self):
        """ helper method - this doesn't get called normally, only when debugging,
        but it acts as a shortcut for doing self._eventmanager.quit() """
        self._eventmanager.quit()

    def _startShutdown(self, naoqi_ok, ctrl_c_pressed):
        """ Do first half of shutdown:
        remove all user pending callbacks (calllaters/event handlers/deferreds)
        start shutdown action (which when complete will call the second half of the
        shutdown)
        """
        self.quitting = True
        do_cleanup = False
        ctrl_c_deferred = None
        quit_deferred = None
        if hasattr(self, '_main_task'):
            if ctrl_c_pressed:
                ctrl_c_deferred = self.onCtrlCPressed()
        quit_deferred = self.onNormalQuit(naoqi_ok)
        if naoqi_ok:
            self.cleanup()
        pending = []
        if quit_deferred:
            pending.append(quit_deferred)
        if ctrl_c_deferred:
            pending.append(ctrl_c_deferred)
        if len(pending) == 0:
            self._completeShutdown()
        else:
            DeferredList(pending).addCallback(self._completeShutdown).addErrback(log.err)

    def _completeShutdown(self, result=None):
        """ Do second half of shutdown:
        stop the single step task.
        reactor shutdown (if we control it)
        """
        info( "CompleteShutdown called:")
        # stop the update task here
        # TODO - should I be worries if this is false?
        if hasattr(self, '_main_task') and self._main_task.running:
            self._main_task.stop()
        # only if we are in charge of the reactor stop that too
        if not self._reactor: return
        self.cleanupAfterNaoqi()
        self._reactor.stop()

    def onTimeStep(self):
        #info( ">>>    twisted burst step     <<<")
        sleep_time = self.doSingleStep()
        if self._eventmanager._should_quit and not self.quitting:
            info( "TwistedMainLoop: event manager initiated quit")
            self._startShutdown(naoqi_ok=True, ctrl_c_pressed=False)

################################################################################

class ExternalMainLoop(BasicMainLoop):

    """ Until twisted is installed on the robot this is the default event loop.
    It basically sleeps and polls. Some intelligence goes into not polling (sending
    socket requests) too much, that happens in World.update.
    """

    def __init__(self, main_behavior_class=None):
        super(ExternalMainLoop, self).__init__(main_behavior_class = main_behavior_class)
        self._keep_the_loop = True

        # need to call burst.init first
        burst.init()

        self.initMainObjectsAndPlayer()
        self.preMainLoopInit() # Start point for Player / GameController
        # Now just call self.doSingleStep

    def profile_filename(self):
        return '%s.kcachegrind' % sys.argv[0].rsplit('.',1)[0]

    def profile_player_filename(self):
        return '%s_player.kcachegrind' % sys.argv[0].rsplit('.',1)[0]

    def _exitApp(self, _):
        self._keep_the_loop = False


################################################################################

from burst_util import is64
if is64() or burst.options.use_pynaoqi:
    MainLoop = TwistedMainLoop
else:
    # default loop doesn't use twisted
    MainLoop = SimpleMainLoop

