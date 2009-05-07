#
# Event enumeration
#

from events import FIRST_EVENT_NUM, LAST_EVENT_NUM, EVENT_STEP

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

    def __init__(self, world):
        """ In charge of computing when certain events happen, keeping track
        of callbacks, and calling them.
        """
        self._events = dict([(event, None) for event in
                xrange(FIRST_EVENT_NUM, LAST_EVENT_NUM)])
        self._world = world

    def register(self, event, callback):
        """ set a callback on an event.
        """
        self._events[event] = callback

    def unregister(self, event):
        self._events[event] = None

    def unregister_all(self):
        for k in self._events.keys():
            self._events[k] = None

    def runonce(self):
        """ Call all callbacks registered based on the new events
        stored in self._world
        """
        for event in self._world.getEvents():
            if self._events[event] != None:
                self._events[event]()
        if self._events[EVENT_STEP]:
            self._events[EVENT_STEP]()
        # TODO: EVENT_TIME_EVENT

class EventManagerLoop(object):
    
    def __init__(self, playerclass):
        """ Must be called after burst.init() - so that any proxies can be
        created at will.
        """
        import actions
        import world
        self._world = world.World()
        self._eventmanager = EventManager(world = self._world)
        self._actions = actions.Actions(world = self._world)
        self._player = playerclass(world = self._world, eventmanager = self._eventmanager,
            actions = self._actions)

    def run(self):
        # a sanity check
        import burst
        try:
            man = burst.ALProxy("Man")
        except:
            print "you are missing the Man proxy - run naoload and uncomment man"
            raise SystemExit
        from time import sleep, time
        # TODO: this should be called from the gamecontroller, this is just
        # a temporary measure. The gamecontroller should keep track of the game state,
        # and when it is changed call the player.
        self._player.onStart()
        while True:
            sleep(0.1)
            self._world.update()
            self._eventmanager.runonce()

