#
# Event Manager, and a main loop
#

import traceback
import sys
from time import time
from heapq import heappush, heappop, heapify

from twisted.python import log

import burst
from burst_util import BurstDeferred, DeferredList

from .events import (FIRST_EVENT_NUM, LAST_EVENT_NUM,
    EVENT_STEP, EVENT_TIME_EVENT)

from burst_consts import EVENT_MANAGER_DT

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

    def resetCallLaters(self):
        del self._call_later[:]

    def callLater(self, dt, callback, *args, **kw):
        """ Will call given callback after an approximation of dt milliseconds,
        specifically:
        REAL_DT = int(dt/EVENT_MANAGER_DT) (int == largest integer that is smaller then)
        """
        # TODO - cancel option? if required then the way is a real Event class
        abstime = self._world.time + max(EVENT_MANAGER_DT, dt)
        heappush(self._call_later, (abstime, callback, args, kw))

    def register(self, callback, event):
        """ set a callback on an event.
        """
        # add to _callbacks
        if callback not in self._callbacks:
            self._callbacks[callback] = set()
        if event in self._callbacks[callback]:
            print "WARNING: harmless register overwrite of %s to %s" % (callback, event)
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
        self._num_registered = 0

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

        # TODO - rename deferreds to burstdeferreds
        events, deferreds = self._world.getEventsAndDeferreds()
        deferreds = list(deferreds) # make copy, avoid endless loop

        # Handle regular events - we keep a copy of the current
        # cb's for all events to make sure there is no loop.
        loop_event_cb = [list(self._events[event]) for event in events]
        for cbs in loop_event_cb:
            for cb in cbs:
                cb()
        # EVENT_STEP registrators are always called (again, list used to create a temp copy)
        for cb in list(self._events[EVENT_STEP]):
            cb()

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

        # flags for external use
        self.finished = False       # True when quit has been called

    def initMainObjectsAndPlayer(self):
        """ Must be called after burst.init() - so that any proxies can be
        created at will.
        """
        import actions
        import world

        # main objects: world, eventmanager, actions and player
        self._world = world.World()
        self._eventmanager = EventManager(world = self._world)
        self._actions = actions.Actions(eventmanager = self._eventmanager)
        self._player = self._playerclass(world = self._world, eventmanager = self._eventmanager,
            actions = self._actions)

    def cleanup(self):
        self.finished = True # set here so an exception later doesn't change it
        self._world.cleanup()

    def setCtrlCCallback(self, ctrl_c_cb):
        self._ctrl_c_cb = ctrl_c_cb

    def run(self):
        """ wrap the actual run in _run to allow profiling - from the command line
        use --profile
        """
        if burst.options.profile:
            print "running via hotshot"
            import hotshot
            filename = "pythongrind.prof"
            prof = hotshot.Profile(filename, lineevents=1)
            prof.runcall(self._run)
            prof.close()
        else:
            self._run()

    def _run(self):
        """ wrap the real loop to catch keyboard interrupt and network errors """
        ctrl_c_pressed, normal_quit = False, True # default is normal_quit so we sit
        if burst.options.catch_player_exceptions:
            try:
                ctrl_c_pressed, normal_quit = self._run_exception_wrap()
            except Exception, e:
                print "caught player exception: %s" % e
                import traceback
                import sys
                traceback.print_tb(sys.exc_info()[2])
        else:
            ctrl_c_pressed, normal_quit = self._run_exception_wrap()
        if ctrl_c_pressed:
            self.onCtrlCPressed()
        if normal_quit:
            self.onNormalQuit()
           
    def onNormalQuit(self):
        if self._actions:
            if burst.options.passive_ctrl_c or not self._world.connected_to_nao:
                print "exiting"
            else:
                print "sitting, removing stiffness and quitting."
                self._sit_deferred = self._actions.sitPoseAndRelax_returnDeferred()
            self._world._gameController.shutdown()
            return True
        print "quitting before starting are we?"
        self.__running_instance = None
        return False

    def onCtrlCPressed(self):
        """ Returns None or the result of the callback, which may be a deferred.
        In that case shutdown will wait for that deferred
        """
        if self._ctrl_c_cb:
            return self._ctrl_c_cb(eventmanager=self._eventmanager, actions=self._actions,
                world=self._world)

    def _run_exception_wrap(self):
        """ returns (ctrl_c_pressed, normal_quit_happened)
        A normal quit is either: Ctrl-C or eventmanager.quit()
        so only non normal quit is a caught exception (uncaught and
        you wouldn't be here)"""
        ctrl_c_pressed, normal_quit = False, True
        try:
            self._run_loop()
        except KeyboardInterrupt:
            print "ctrl-c detected."
            ctrl_c_pressed = True
        except RuntimeError, e:
            print "naoqi exception caught:", e
            print "quitting"
            normal_quit = False
        return ctrl_c_pressed, normal_quit

    def preMainLoopInit(self):
        """ call once before the main loop """
        self._player.onStart()
        self.main_start_time = time()
        self.cur_time = self.main_start_time
        self.next_loop = self.cur_time

    def doSingleStep(self):
        """ call once for every loop iteration
        TODO: This is just using a polling loop to emulate real
        event generation, once twisted is really used this should
        become mute, and twisted will call the eventmanager directly.
        eventmanager will then probably register directly with twisted.

        returns the amount of time to sleep in seconds
        """
        if burst.options.trace_proxies:
            ball = self._world.ball.seen and 'B' or ' '
            yglp = self._world.yglp.seen and 'L' or ' '
            ygrp = self._world.ygrp.seen and 'R' or ' '
            # LINE_UP is to line up with the LogCalls object.
            LINE_UP = 62
            print "%3.2f  %s%s%s%02d%s" % (self.cur_time - self.main_start_time, ball, yglp, ygrp,
                len(self._eventmanager._call_later), "-"*LINE_UP)
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

        # need to call burst.init first
        burst.init()

        self.initMainObjectsAndPlayer()

    def _run_loop(self):
        import burst
        print "running custom event loop with sleep time of %s milliseconds" % (EVENT_MANAGER_DT*1000)
        from time import sleep, time
        # TODO: this should be called from the gamecontroller, this is just
        # a temporary measure. The gamecontroller should keep track of the game state,
        # and when it is changed call the player.
        self.preMainLoopInit()
        while True:
            sleep_time = self.doSingleStep()
            if self._eventmanager._should_quit:
                break
            if sleep_time:
                sleep(sleep_time)
        self.cleanup()

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
                self._startShutdown(normal_quit=True, ctrl_c_pressed=True)
            else:
                print "Two ctrl-c - shutting down uncleanly"
                orig_sigInt(*args)

        reactor.sigInt = my_int_handler

        import pynaoqi
        self.con = pynaoqi.getDefaultConnection()
        self.started = False        # True when setStartCallback has been called
        if startRightNow:
            self.start()

    def start(self):
        self.con.modulesDeferred.addCallback(self._twistedStart).addErrback(log.err)
        self.started = True

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

    def _startShutdown(self, normal_quit, ctrl_c_pressed):
        # Stop our task loop
        do_cleanup = False
        ctrl_c_deferred = None
        if hasattr(self, '_main_task'):
            if ctrl_c_pressed:
                ctrl_c_deferred = self.onCtrlCPressed()
            if normal_quit:
                do_cleanup = self.onNormalQuit()
            if self._main_task.running: # TODO - should I be worries if this is false?
                self._main_task.stop()
        if do_cleanup:
            # only reason not to is if we didn't complete initialization to begin with
            self.cleanup()
        pending = []
        if hasattr(self, '_sit_deferred'):
            pending.append(self._sit_deferred)
        if ctrl_c_deferred:
            pending.append(ctrl_c_deferred)
        if len(pending) == 0:
            self._completeShutdown()
        else:
            DeferredList(pending).addCallback(self._completeShutdown)

    def _completeShutdown(self, result=None):
        print "CompleteShutdown called:"
        if not self._control_reactor: return
        from twisted.internet import reactor
        reactor.stop()

    def onTimeStep(self):
        #print ">>>    twisted burst step     <<<"
        sleep_time = self.doSingleStep()
        if self._eventmanager._should_quit:
            print "TwistedMainLoop: event manager initiated quit"
            self._startShutdown(normal_quit=True, ctrl_c_pressed=False)

################################################################################

from burst_util import is64
if is64() or burst.options.use_pynaoqi:
    MainLoop = TwistedMainLoop
else:
    # default loop doesn't use twisted
    MainLoop = SimpleMainLoop

