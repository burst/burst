#
# Event Manager, and a main loop
#

import traceback
import sys
from time import time
from heapq import heappush, heappop, heapify

from twisted.python import log

import burst
from burst_util import BurstDeferred, DeferredList, Deferred

from .events import (FIRST_EVENT_NUM, LAST_EVENT_NUM,
    EVENT_STEP, EVENT_TIME_EVENT)

from burst_consts import EVENT_MANAGER_DT
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
            eventmanager.register(event, lambda self=self, event=event: self.onEvent(event))
            
    def onEvent(self, event):
        self._waiting.remove(event)
        if len(self._waiting) == 0:
            for event in self.events:
                self._eventmanager.unregister(event)
            self._cb()

################################################################################

class SerialEvent(SuperEvent):
    
    def __init__(self, eventmanager, events, callbacks):
        super(SerialEvent, self).__init__(eventmanager, events)
        self._callbacks = callbacks
        self._i = 0
        eventmanager.register(self._events[0], self.onEvent)
            
    def onEvent(self, event):
        self._eventmanager.unregister(self._events[self._i])
        self._callbacks[self._i]()
        self._i += 1
        if len(self._events) == self._i:
            return
        self._eventmanager.register(self._events[self._i], self.onEvent)

################################################################################

class EventManager(object):
    """ Class to handle all event routing. Mainly we have:
    anything in burst.events can be called with EventManager.register

    due to lack of time time events are the same, so you only have one
    and no support right now for multiple requestors (do that in your code
    you lazy bum)
    """

    verbose = burst.options.verbose_eventmanager

    def __init__(self, world):
        """ In charge of computing when certain events happen, keeping track
        of callbacks, and calling them.
        """
        # The _events maps from an event enum to a set of callbacks (so order
        # of callback is undefined)
        self._events = dict([(event, set()) for event in
                xrange(FIRST_EVENT_NUM, LAST_EVENT_NUM)])
        self._callbacks = {} # dictionary from callback to events set it is registered to
        self._world = world
        self._should_quit = False
        self._call_later = [] # heap of tuples: absolute_time, callback, args, kw
        self.unregister_all()

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
        REAL_DT = int(dt/EVENT_MANAGER_DT) (int == largest integer that is smaller then)
        """
        # TODO - cancel option? if required then the way is a real Event class
        abstime = self._world.time + max(EVENT_MANAGER_DT, dt)
        heappush(self._call_later, (abstime, callback, args, kw))

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

    def handlePendingEventsAndDeferreds(self):
        """ Call all callbacks registered based on the new events
        stored in self._world

        Also handles callLaters
        """
        # Implementation note: we need to avoid endless loops in here.
        # this can happen if, for instance, one of the callLater callbacks
        # creates another callLater during the callLater loop.
        # So to avoid stuff like that with the deferreds too (events are
        # too simple for this to happen) we create a copy of the lists
        # and loop on them.

        # Code handling this "removal in cb" is noted as "handle possible removal"
        # to make the code more readable.

        # TODO - rename deferreds to burstdeferreds
        events, deferreds = self._world.getEventsAndDeferreds()
        deferreds = list(deferreds) # make copy, avoid endless loop

        # Handle regular events - we keep a copy of the current
        # cb's for all events to make sure there is no loop.
        loop_event_cb = [(event, list(self._events[event])) for event in events]
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

        # Handle call later's
        cur_call_later = self._call_later
        self._call_later = [] # new heap for anything created by the callbacks themselves,
                              # avoid endless loops.
        while len(cur_call_later) > 0:
            next_time = cur_call_later[0][0]
            if self.verbose:
                print "EventManager: we have some callLaters"
            if next_time <= self._world.time:
                next_time, cb, args, kw = heappop(cur_call_later)
                if self.verbose:
                    print "EventManager: calling callLater callback"
                cb(*args, **kw)
            else:
                break # VERY IMPORTANT..
        # now merge the new with the old
        if len(self._call_later) > 0:
            if self.verbose:
                print "EventManager: callLater-cbs added callLaters! merging"
            self._call_later = cur_call_later + self._call_later
            heapify(self._call_later) # TODO - implement merge, this is faster.
        else:
            self._call_later = cur_call_later

        # Handle deferreds
        for deferred in deferreds:
            deferred.callOnDone()

################################################################################

class BasicMainLoop(object):
    
    __running_instance = None

    def __init__(self, playerclass):
        self._playerclass = playerclass
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
        self._actions = actions.Actions(eventmanager = self._eventmanager)
        self._player = self._playerclass(world = self._world, eventmanager = self._eventmanager,
            actions = self._actions)

    def cleanup(self):
        self.finished = True # set here so an exception later doesn't change it
        self._world.cleanup()

    def onNormalQuit(self):
        d = None
        if self._actions:
            if burst.options.passive_ctrl_c:# or not self._world.connected_to_nao:
                print "BasicMainLoop: exiting"
            else:
                print "BasicMainLoop: sitting, removing stiffness and quitting."
                d = self._actions.sitPoseAndRelax_returnDeferred()
            self._world._gameController.shutdown() # in parallel to sitting
        if not d:
            print "BasicMainLoop: quitting before starting are we?"
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
        print "Time Objs-CL|IN|PO|YRt          |YLt          |Ball         |Out|Inc|".ljust(burst_consts.CONSOLE_LINE_LENGTH, '-')
        print "="*burst_consts.CONSOLE_LINE_LENGTH

    def _printTraceTicker(self):
        ball = self._world.ball.seen and 'B' or ' '
        yglp = self._world.yglp.seen and 'L' or ' '
        ygrp = self._world.ygrp.seen and 'R' or ' '
        targets = self._actions.searcher._targets
        def getjoints(obj):
            if obj not in targets: return '-----------'
            r = obj.centered_self
            if not r.sighted: return '           '
            return ('%0.2f %0.2f %s' % (r.head_yaw, r.head_pitch, r.sighted_centered and 'T' or 'F')).rjust(11)
        yglp_joints = getjoints(self._world.yglp)
        ygrp_joints = getjoints(self._world.ygrp)
        ball_joints = getjoints(self._world.ball)
        num_out = self._getNumberOutgoingMessages()
        num_in = self._getNumberIncomingMessages()
        # LINE_UP is to line up with the LogCalls object.
        LINE_UP = 62
        print ("%3.2f  %s%s%s-%02d|%02d|%02d|%s|%s|%s|%3d|%3d|" % (self.cur_time - self.main_start_time,
            ball, yglp, ygrp,
            len(self._eventmanager._call_later),
            len(self._world._movecoordinator._initiated),
            len(self._world._movecoordinator._posted),
            ygrp_joints, yglp_joints, ball_joints,
            num_out, num_out - num_in,
            )).ljust(burst_consts.CONSOLE_LINE_LENGTH, '-')

    def preMainLoopInit(self):
        """ call once before the main loop """
        self.main_start_time = time()
        self.cur_time = self.main_start_time
        self.next_loop = self.cur_time
        if burst.options.trace_proxies:
            self._printTraceTickerHeader()
        # First do a single world update - get values for all variables, etc.
        self.doSingleStep()
        # Second, queue player.
        self._player.onStart()

    def doSingleStep(self):
        """ call once for every loop iteration
        TODO: This is just using a polling loop to emulate real
        event generation, once twisted is really used this should
        become mute, and twisted will call the eventmanager directly.
        eventmanager will then probably register directly with twisted.

        returns the amount of time to sleep in seconds
        """
        if burst.options.trace_proxies:
            self._printTraceTicker()

        self._eventmanager.handlePendingEventsAndDeferreds()
        self._world.collectNewUpdates(self.cur_time)
        self.next_loop += EVENT_MANAGER_DT
        self.cur_time = time()
        if self.cur_time > self.next_loop:
#            print "WARNING: loop took %0.3f ms" % (
#                (self.cur_time - self.next_loop + EVENT_MANAGER_DT
#                ) * 1000)
#            self.next_loop = self.cur_time
            return None
        else:
            return self.next_loop - self.cur_time

################################################################################

class SimpleMainLoop(BasicMainLoop):

    """ Until twisted is installed on the robot this is the default event loop.
    It basically sleeps and polls. Some intelligence goes into not polling (sending
    socket requests) too much, that happens in World.update.
    """

    def __init__(self, playerclass):
        super(SimpleMainLoop, self).__init__(playerclass = playerclass)
        self._keep_the_loop = True

        # need to call burst.init first
        burst.init()

        self.initMainObjectsAndPlayer()

    def run(self):
        """ wrap the actual run in _run to allow profiling - from the command line
        use --profile
        """
        if burst.options.profile:
            print "running via hotshot"
            import hotshot
            filename = "pythongrind.prof"
            prof = hotshot.Profile(filename, lineevents=1)
            prof.runcall(self._run_loop)
            prof.close()
        else:
            self._run_loop()

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
        print "running custom event loop with sleep time of %s milliseconds" % (EVENT_MANAGER_DT*1000)
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
                if naoqi_ok:
                    d = self.onNormalQuit()
                    if d:
                        d.addCallback(self._exitApp)
            if sleep_time:
                sleep(sleep_time)

    def _exitApp(self, _):
        self._keep_the_loop = False

################################################################################

class TwistedMainLoop(BasicMainLoop):

    def __init__(self, playerclass, control_reactor=True, startRightNow=True):
    
        super(TwistedMainLoop, self).__init__(playerclass = playerclass)
        self._do_cleanup = True
        self._control_reactor = control_reactor

        from twisted.internet import reactor
        orig_sigInt = reactor.sigInt
        self._ctrl_c_presses = 0
        def my_int_handler(reactor, *args):
            self._ctrl_c_presses += 1
            print "TwistedMainLoop: SIGBREAK caught"
            if self._ctrl_c_presses == 1:
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
        self._main_task = task.LoopingCall(self.onTimeStep)
        self._main_task.start(EVENT_MANAGER_DT)

    def _run_loop(self):
        pass # we override run too, work is done there.

    def run(self):
        if not self._control_reactor:
            print "TwistedMainLoop: not in control of reactor"
            return
        print "\nrunning TWISTED event loop with sleep time of %s milliseconds" % (EVENT_MANAGER_DT*1000)
        from twisted.internet import reactor
        reactor.run() #installSignalHandlers=0)
        print "TwistedMainLoop: event loop done"

    def shutdown(self):
        """ helper method - this doesn't get called normally, only when debugging,
        but it acts as a shortcut for doing self._eventmanager.quit() """
        self._eventmanager.quit()

    def _startShutdown(self, naoqi_ok, ctrl_c_pressed):
        # Stop our task loop
        do_cleanup = False
        ctrl_c_deferred = None
        quit_deferred = None
        if hasattr(self, '_main_task'):
            if ctrl_c_pressed:
                ctrl_c_deferred = self.onCtrlCPressed()
            if naoqi_ok:
                quit_deferred = self.onNormalQuit()
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
        print "CompleteShutdown called:"
        # stop the update task here
        # TODO - should I be worries if this is false?
        if hasattr(self, '_main_task') and self._main_task.running:
            self._main_task.stop()
        # only if we are in charge of the reactor stop that too
        if not self._control_reactor: return
        from twisted.internet import reactor
        reactor.stop()

    def onTimeStep(self):
        #print ">>>    twisted burst step     <<<"
        sleep_time = self.doSingleStep()
        if self._eventmanager._should_quit and not self.quitting:
            print "TwistedMainLoop: event manager initiated quit"
            self.quitting = True
            self._startShutdown(naoqi_ok=True, ctrl_c_pressed=False)

################################################################################

from burst_util import is64
if is64() or burst.options.use_pynaoqi:
    MainLoop = TwistedMainLoop
else:
    # default loop doesn't use twisted
    MainLoop = SimpleMainLoop

