#
# Event Manager, and a main loop
#

import traceback
import sys
import os
from time import time
from heapq import heappush, heappop, heapify

from twisted.python import log

import burst
from burst_util import DeferredList, func_name, Profiler, succeed
import burst_util
import burst.actions
from burst.player import Player

from burst_events import (FIRST_EVENT_NUM, LAST_EVENT_NUM,
    EVENT_STEP, EVENT_TIME_EVENT)

import burst_consts

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
                    print "CAUGHT EXCEPTION: %s" % e
                self._eventmanager.unregister(event, onEvent)
                print "singletime: unregistering from %s" % event
            print "singletime: registering to %s" % event
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
    anything in burst.events can be called with EventManager.register

    due to lack of time time events are the same, so you only have one
    and no support right now for multiple requestors (do that in your code
    you lazy bum)
    """

    def __init__(self, world):
        """ In charge of computing when certain events happen, keeping track
        of callbacks, and calling them.
        """
        # The _events maps from an event enum to a set of callbacks (so order
        # of callback is undefined)
        self.verbose = burst.options.verbose_eventmanager
        self.num_callbacks_to_report = 2
        self._clearEventsAndCallbacks()
        self._world = world
        self.burst_deferred_maker = self._world.burst_deferred_maker
        self._should_quit = False
        self._call_later = [] # heap of tuples: absolute_time, callback, args, kw

        self.dt = burst.options.dt # THA time step. defaults to 50ms, but we are trying other values.

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
        if callback in self._call_later:
            self._call_later.remove(callback)

    def register(self, callback, event):
        """ set a callback on an event.
        """
        # add to _callbacks
        if callback not in self._callbacks:
            self._callbacks[callback] = set()
        if event in self._callbacks[callback]:
            print "WARNING: harmless re-register of %s to %s" % (callback, event)
        self._callbacks[callback].add(event)
        # add to _events
        self._events[event].add(callback)
        if self.verbose:
            print "EventManager: #_events[%d] = %s" % (event, len(self._events[event]))

    def register_oneshot(self, callback, event):
        def on_one_event():
            if self.verbose:
                print "EventManager: one shot removal, before: %s, %s" % (
                            len(self._events[event]), self._events[event])
            self.unregister(on_one_event, event)
            if self.verbose:
                print "EventManager: one shot removal, after: %s, %s" % (
                            len(self._events[event]), self._events[event])
            callback()
        on_one_event.func_name = 'on_one_event__%s' % (func_name(callback))
        self.register(on_one_event, event)

    def unregister(self, callback, event=None):
        """Unregister the callback function callback, if event is given then from that
        event only, otherwise from all events it is registered for. If it isn't registered
        to anything then nothing will happen.
        """
        if self.verbose:
            print "EventManager: unregister %s" % callback
        if callback in self._callbacks:
            # remove from _events
            for event in self._callbacks[callback]:
                self._events[event].remove(callback)
            # remove from _callbacks
            del self._callbacks[callback]

    def unregister_all(self):
        for k in self._events.keys():
            self._events[k] = set()

    def quit(self):
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
                print "EventManager: we have some callLaters"
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
            print 'EventManager: you have %s = %s D + %s E + %s S + %s L cbs' % self.getPendingBreakdown() 

    def getPendingBreakdown(self):
        return (self._num_cbs_in_round, self._num_deferreds, self._num_events, self._num_time_step,
                self._num_call_laters)

    def numberPendingCallbacks(self):
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
                    cb()
                elif self.verbose:
                    print "EventManager: %s removed by prior during step" % cb
        # EVENT_STEP registrators are always called (again, list used to create a temp copy)
        for cb in list(self._events[EVENT_STEP]):
            if cb in self._events[EVENT_STEP]: # handle possible removal
                cb()
            elif self.verbose:
                print "EventManager: %s removed by prior during step" % cb

        # Handle call later's (we counted before, now we run and merge)
        for cb, args, kw in call_laters_this_frame:
            if self.verbose:
                print "EventManager: calling callLater callback"
            cb(*args, **kw)

        # now merge the new with the old
        if len(self._call_later) > 0:
            if self.verbose:
                print "EventManager: callLater-cbs added callLaters! merging"
            self._call_later = self._current_call_later + self._call_later
            heapify(self._call_later) # TODO - implement merge, this is faster.
        else:
            self._call_later = self._current_call_later

        # Handle deferreds
        for deferred in deferreds:
            deferred.callOnDone()

################################################################################

class BasicMainLoop(object):
    
    __running_instance = None

    def __init__(self, main_behavior_class):
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

        self._dt = None # we get this from constructing eventmanager - kinda crooked

        # flags for external use
        self.finished = False       # True when quit has been called
        self._on_normal_quit_called = False

        self._profiler = None
        
        # debug flags
        self._ticker = burst.options.ticker or burst.options.trace_proxies

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
        self._eventmanager = EventManager(world = self._world)
        self._dt = self._eventmanager.dt
        self._actions = actions.Actions(eventmanager = self._eventmanager)
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
            print "HARMLESS ERROR: second BaseMainLoop.onNormalQuit called"
            return
        self._on_normal_quit_called = True
        self._on_normal_quit__naoqi_ok = naoqi_ok
        stop_deferred = None
        if self._player:
            stop_deferred = self._player.onStop()

        # From this point onwards illegal moves (i.e. anything) are allowed.
        print "MainLoop: ILLEGAL moves ALLOWED from now on"
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
                print "BasicMainLoop: exiting"
            else:
                if naoqi_ok:
                    print "BasicMainLoop: sitting, removing stiffness and quitting."
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

    def _printTraceTickerHeader(self):
        print "="*burst_consts.CONSOLE_LINE_LENGTH
        print "Time Objs-CL|IN|PO|Right        |Left         |Ball         |Out|Inc|".ljust(burst_consts.CONSOLE_LINE_LENGTH, '-')
        print "="*burst_consts.CONSOLE_LINE_LENGTH

    def _printTraceTicker(self):
        ball = self._world.ball.seen and 'B' or ' '
        yglp = self._world.yglp.seen and 'L' or ' '
        ygrp = self._world.ygrp.seen and 'R' or ' '
        unknown_yellow = self._world.yellow_goal.unknown.seen and 'U' or ' '
        bglp = self._world.bglp.seen and 'l' or ' '
        bgrp = self._world.bgrp.seen and 'r' or ' '
        unknown_blue = self._world.blue_goal.unknown.seen and 'u' or ' '
        targets = self._actions.searcher.targets
        def getjoints(obj):
            if obj not in targets: return False
            r = obj.centered_self
            if not r.sighted: return '             '
            return ('%0.2f %0.2f %s' % (r.head_yaw, r.head_pitch, r.sighted_centered and 'T' or 'F')).rjust(11)
        left_joints = getjoints(self._world.yglp) or getjoints(self._world.bglp) or '-------------'
        right_joints = getjoints(self._world.ygrp) or getjoints(self._world.bgrp) or '-------------'
        ball_joints = getjoints(self._world.ball)
        num_out = self._getNumberOutgoingMessages()
        num_in = self._getNumberIncomingMessages()
        total, deferreds, event_cbs, step_cbs, calllater_cbs = self._eventmanager.getPendingBreakdown()
        # LINE_UP is to line up with the LogCalls object.
        LINE_UP = 62
        print ("%4.1f %s%s%s%s%s%s%s-%02d|%02d|%02d|%s|%s|%s|%3d|%3d|%s D %s E %s S %s L|%s" % (self.cur_time - self.main_start_time,
            ball,
            yglp, ygrp, unknown_yellow,
            bglp, bgrp, unknown_blue,
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
            print "MainLoop: only LEGAL moves allowed from now on"
            self._player.onStart()
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
        if burst.options.trace_proxies or (self._ticker and self._eventmanager.numberPendingCallbacks() > 0):
            self._printTraceTicker()

        # reverse the order? arg.
        if burst.options.profile_player:
            self._profiler.runcall(self._eventmanager.handlePendingCallbacks)
        else:
            self._eventmanager.handlePendingCallbacks()
        self._world.collectNewUpdates(self.cur_time)
        self.next_loop += self._dt
        self.cur_time = time()
        if self.cur_time > self.next_loop:
#            print "WARNING: loop took %0.3f ms" % (
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

    def __init__(self, main_behavior_class):
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
            except Exception, e:
                print "BasicMainLoop: caught player exception: %s" % e
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
            print "BasicMainLoop: naoqi exception caught:", e
            print "BasicMainLoop: quitting"
            naoqi_ok = False
            if 'SOAP:Connection refused' in str(e):
                print "Naoqi quit (SOAP:Connection refused), exiting."
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
            print "BasicMainLoop: ctrl-c detected."
            ctrl_c_pressed = True
        # No ctrl-c here I hope
        if ctrl_c_pressed:
            try:
                self.onCtrlCPressed()
                self._run_loop_helper() # continue the loop, wait for pending moves etc.
            except KeyboardInterrupt:
                print "BasicMainLoop: ctrl-c detected a second time. unclean exit."
                raise SystemExit

    def _run_loop_helper(self):
        import burst
        print "running custom event loop with sleep time of %s milliseconds" % (self._dt*1000)
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
                    d.addCallback(self.cleanupAfterNaoqi)
                    d.addCallback(self._exitApp)
            if sleep_time:
                sleep(sleep_time)

    def _exitApp(self, _):
        self._keep_the_loop = False

################################################################################

class TwistedMainLoop(BasicMainLoop):

    def __init__(self, main_behavior_class, control_reactor=True, startRightNow=True):
        super(TwistedMainLoop, self).__init__(main_behavior_class = main_behavior_class)
        self._do_cleanup = True
        self._control_reactor = control_reactor

        from twisted.internet import reactor
        orig_sigInt = reactor.sigInt
        self._ctrl_c_presses = 0
        def my_int_handler(reactor, *args):
            self._ctrl_c_presses += 1
            print "TwistedMainLoop: SIGBREAK caught"
            if self._ctrl_c_presses == 1:
                if self.quitting:
                    print "TwistedMainLoop: SIGBREAK: quitting already in progress"
                else:
                    self._startShutdown(naoqi_ok=True, ctrl_c_pressed=True)
            else:
                print "Two ctrl-c - shutting down uncleanly"
                orig_sigInt(*args)

        reactor.sigInt = my_int_handler

        import pynaoqi
        self.con = pynaoqi.getDefaultConnection()
        self.started = False        # True when setStartCallback has been called
        self.quitting = False
        if startRightNow:
            self.start()

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
        print "TwistedMainLoop: _twistedStart"
        self.initMainObjectsAndPlayer()
        print "TwistedMainLoop: created main objects"
        from twisted.internet import reactor, task
        self.preMainLoopInit()
        print "\nrunning TWISTED event loop with sleep time of %s milliseconds" % (self._dt*1000)
        self._main_task = task.LoopingCall(self.onTimeStep)
        self._main_task.start(self._dt)

    def _run_loop(self):
        if not self._control_reactor:
            print "TwistedMainLoop: not in control of reactor"
            return
        from twisted.internet import reactor
        reactor.run() #installSignalHandlers=0)
        print "TwistedMainLoop: event loop done"

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
            DeferredList(pending).addCallback(self._completeShutdown)

    def _completeShutdown(self, result=None):
        """ Do second half of shutdown:
        stop the single step task.
        reactor shutdown (if we control it)
        """
        print "CompleteShutdown called:"
        # stop the update task here
        # TODO - should I be worries if this is false?
        if hasattr(self, '_main_task') and self._main_task.running:
            self._main_task.stop()
        # only if we are in charge of the reactor stop that too
        if not self._control_reactor: return
        from twisted.internet import reactor
        self.cleanupAfterNaoqi()
        reactor.stop()

    def onTimeStep(self):
        #print ">>>    twisted burst step     <<<"
        sleep_time = self.doSingleStep()
        if self._eventmanager._should_quit and not self.quitting:
            print "TwistedMainLoop: event manager initiated quit"
            self._startShutdown(naoqi_ok=True, ctrl_c_pressed=False)

################################################################################

from burst_util import is64
if is64() or burst.options.use_pynaoqi:
    MainLoop = TwistedMainLoop
else:
    # default loop doesn't use twisted
    MainLoop = SimpleMainLoop

