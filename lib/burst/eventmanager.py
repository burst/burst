#
# Event Manager, and a main loop
#

import traceback
import sys
from time import time

import burst
from burst_util import BurstDeferred, DeferredList

from .events import (FIRST_EVENT_NUM, LAST_EVENT_NUM,
    EVENT_STEP, EVENT_TIME_EVENT)

from .consts import EVENT_MANAGER_DT

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
        self._events = dict([(event, None) for event in
                xrange(FIRST_EVENT_NUM, LAST_EVENT_NUM)])
        self._world = world
        self._should_quit = False
        self.unregister_all()
        self.setTimeoutEventParams(0.0)

    def setTimeoutEventParams(self, dt, oneshot=False, cb=None):
        """ Set Timeout Parameters.
        dt is in seconds. if oneshot is true the registration
        will be deleted after a single callback.

        When this is set the next timeout is scheduled to current time
        taken from world plus dt (i.e. self._world.time + dt)
        """
        self._timeout_dt = dt
        self._timeout_oneshot = oneshot
        self._timeout_last = self._world.time
        print "setting timeout event, start time =", self._timeout_last
        if cb: # shortcut
            self._events[EVENT_TIME_EVENT] = cb

    def register(self, event, callback):
        """ set a callback on an event.
        """
        if not self._events[event]:
            self._num_registered += 1
        else:
            if self._events[event] is callback:
                print "WARNING: harmless register overwrite of event %s" % event
            else:
                print "WARNING: overwriting register for event %s with %s (old was %s)" % (event, callback, self._events[event])
        self._events[event] = callback

    def unregister(self, event):
        if self._events[event]:
            self._num_registered -= 1
            self._events[event] = None

    def unregister_all(self):
        for k in self._events.keys():
            self._events[k] = None
        self._num_registered = 0

    def quit(self):
        self._should_quit = True

    def handlePendingEventsAndDeferreds(self):
        """ Call all callbacks registered based on the new events
        stored in self._world
        """
        events, deferreds = self._world.getEventsAndDeferreds()
        for event in events:
            if self._events[event] != None:
                self._events[event]()
        if self._events[EVENT_STEP]:
            self._events[EVENT_STEP]()
        if self._events[EVENT_TIME_EVENT]:
            if self._timeout_last + self._timeout_dt <= self._world.time:
                self._events[EVENT_TIME_EVENT]()
                self._timeout_last = self._world.time
                if self._timeout_oneshot:
                    self._events[EVENT_TIME_EVENT] = None
        for deferred in deferreds:
            deferred.callOnDone()

class BasicMainLoop(object):
    
    def __init__(self, playerclass):
        self._playerclass = playerclass
        self._ctrl_c_cb = None
        self._actions = None

    def initMainObjectsAndPlayer(self):
        """ Must be called after burst.init() - so that any proxies can be
        created at will.
        """
        import actions
        import world

        # need to call burst.init first (also, this kinda makes sure
        # there is only one EventManagerLoop)
        burst.init()

        # main objects: world, eventmanager, actions and player
        self._world = world.World()
        self._eventmanager = EventManager(world = self._world)
        self._actions = actions.Actions(world = self._world)
        self._player = self._playerclass(world = self._world, eventmanager = self._eventmanager,
            actions = self._actions)

    def cleanup(self):
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
                print "caught player exception:"
                if hasattr(sys, 'last_traceback'):
                    traceback.print_tb(sys.last_traceback)
                else:
                    print "no traceback, bare exception:", e
        else:
            ctrl_c_pressed, normal_quit = self._run_exception_wrap()
        if ctrl_c_pressed:
            self.onCtrlCPressed()
        if normal_quit:
            self.onNormalQuit()
           
    def onNormalQuit(self):
        if self._actions:
            print "sitting, removing stiffness and quitting."
            self._sit_deferred = self._actions.sitPoseAndRelax()
            return True
        print "quitting before starting are we?"
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
            # the strange number 66 is to line up with the LogCalls object.
            print "%3.3f  %s" % (self.cur_time - self.main_start_time, "-"*66)
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

class SimpleMainLoop(BasicMainLoop):

    """ Until twisted is installed on the robot this is the default event loop.
    It basically sleeps and polls. Some intelligence goes into not polling (sending
    socket requests) too much, that happens in World.update.
    """

    def __init__(self, playerclass):
        super(SimpleMainLoop, self).__init__(playerclass = playerclass)
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

class TwistedMainLoop(BasicMainLoop):

    def __init__(self, playerclass):
    
        super(TwistedMainLoop, self).__init__(playerclass = playerclass)
        self._do_cleanup = True

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
        self.con.modulesDeferred.addCallback(self._twistedStart)

    def _twistedStart(self, _):
        self.initMainObjectsAndPlayer()
        from twisted.internet import reactor, task
        self.preMainLoopInit()
        self._main_task = task.LoopingCall(self.onTimeStep)
        self._main_task.start(EVENT_MANAGER_DT)

    def _run_loop(self):
        pass # we override run too, work is done there.

    def run(self):
        print "\nrunning TWISTED event loop with sleep time of %s milliseconds" % (EVENT_MANAGER_DT*1000)
        from twisted.internet import reactor
        reactor.run() #installSignalHandlers=0)
        print "TwistedMainLoop: event loop done"

    def _startShutdown(self, normal_quit, ctrl_c_pressed):
        # Stop our task loop
        do_cleanup = False
        ctrl_c_deferred = None
        if hasattr(self, '_main_task'):
            if ctrl_c_pressed:
                ctrl_c_deferred = self.onCtrlCPressed()
            if normal_quit:
                do_cleanup = self.onNormalQuit()
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
        from twisted.internet import reactor
        reactor.stop()

    def onTimeStep(self):
        #print ">>>    twisted burst step     <<<"
        sleep_time = self.doSingleStep()
        if self._eventmanager._should_quit:
            print "TwistedMainLoop: event manager initiated quit"
            self._startShutdown(normal_quit=True, ctrl_c_pressed=False)

from burst_util import is64
if is64() or burst.options.use_pynaoqi:
    MainLoop = TwistedMainLoop
else:
    # default loop doesn't use twisted
    MainLoop = SimpleMainLoop

