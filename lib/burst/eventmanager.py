#
# Event enumeration
#

from events import FIRST_EVENT_NUM, LAST_EVENT_NUM, EVENT_STEP

EVENT_MANAGER_DT = 0.05

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

def expected_argument_count(f):
    if hasattr(f, 'im_func'):
        return f.im_func.func_code.co_argcount - 1 # to account for self
    return f.func_code.co_argcount

class Deferred(object):
    
    """ A Deferred is a promise to call you when some operation is complete.
    It is also concatenatable. What that means for implementation, is that
    when the operation is done we need to call a deferred we stored and gave
    the user when he gave us a callback. That deferred 
    """
    we_the_people = []

    def __init__(self, data, parent=None):
        self._data = data
        self._ondone = None
        self._completed = False # we need this for concatenation to work
        self._parent = parent # DEBUG only
        Deferred.we_the_people.append(self)
    
    def onDone(self, cb):
        # TODO: shortcutting. How the fuck do I call the cb immediately without
        # giving a chance to the caller to use the chain_deferred??

        # will be called by cb's return deferred, if any
        chain_deferred = Deferred(data = None, parent=self)
        self._ondone = (cb, chain_deferred)
        return chain_deferred

    def callOnDone(self):
        self._completed = True
        if self._ondone:
            cb, chain_deferred = self._ondone
            if expected_argument_count(cb) == 0:
                ret = cb()
            else:
                ret = cb(self._data)
            # is it a deferred? if so tell it to execute the deferred
            # we handed out once it is done.
            if isinstance(ret, Deferred):
                ret.onDone(chain_deferred.callOnDone)

class EventManager(object):

    def __init__(self, world):
        """ In charge of computing when certain events happen, keeping track
        of callbacks, and calling them.
        """
        self._events = dict([(event, None) for event in
                xrange(FIRST_EVENT_NUM, LAST_EVENT_NUM)])
        self._world = world
        self._should_quit = False
        self.unregister_all()

    def register(self, event, callback):
        """ set a callback on an event.
        """
        if not self._events[event]:
            self._num_registered += 1
            print "WARNING: overwriting register for event %s with %s" % (event, callback)
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

    def runonce(self):
        """ Call all callbacks registered based on the new events
        stored in self._world
        """
        events, deferreds = self._world.getEventsAndDeferreds()
        for event in events:
            if self._events[event] != None:
                self._events[event]()
        if self._events[EVENT_STEP]:
            self._events[EVENT_STEP]()
        # TODO: EVENT_TIME_EVENT
        for deferred in deferreds:
            deferred.callOnDone()

class EventManagerLoop(object):
    
    def __init__(self, playerclass):
        """ Must be called after burst.init() - so that any proxies can be
        created at will.
        """
        import actions
        import world

        # main objects: world, eventmanager, actions and player
        self._world = world.World()
        self._eventmanager = EventManager(world = self._world)
        self._actions = actions.Actions(world = self._world)
        self._player = playerclass(world = self._world, eventmanager = self._eventmanager,
            actions = self._actions)

    def run(self):
        """ wrap the actual run in _run to allow profiling - from the command line
        use --profile
        """
        import burst.base
        if burst.base.options.profile:
            print "running via hotshot"
            import hotshot
            filename = "pythongrind.prof"
            prof = hotshot.Profile(filename, lineevents=1)
            prof.runcall(self._run)
            prof.close()
        else:
            self._run()

    def _run(self):
        # a sanity check
        import burst
        try:
            man = burst.ALProxy("Man")
        except:
            print "you are missing the Man proxy - run naoload and uncomment man"
            raise SystemExit
        print "running custom event loop with sleep time of %s milliseconds" % (EVENT_MANAGER_DT*1000)
        from time import sleep, time
        # TODO: this should be called from the gamecontroller, this is just
        # a temporary measure. The gamecontroller should keep track of the game state,
        # and when it is changed call the player.
        self._player.onStart()
        self.main_start_time = time()
        cur_time = self.main_start_time
        next_loop = cur_time
        while True:
            self._world.update(cur_time)
            self._eventmanager.runonce()
            if self._eventmanager._should_quit:
                break
            next_loop += EVENT_MANAGER_DT
            cur_time = time()
            if cur_time > next_loop:
                print "WARNING: loop took %s time" % (cur_time - next_loop - EVENT_MANAGER_DT)
                next_loop = cur_time
            else:
                sleep(next_loop - cur_time)

