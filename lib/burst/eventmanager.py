#
# Event enumeration
#

from events import FIRST_EVENT_NUM, LAST_EVENT_NUM, EVENT_STEP

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
        self._actions = actions.Actions()
        self._player = playerclass(world = self._world, eventmanager = self._eventmanager,
            actions = self._actions)

    def run(self):
        from time import sleep, time
        # TODO: this should be called from the gamecontroller, this is just
        # a temporary measure. The gamecontroller should keep track of the game state,
        # and when it is changed call the player.
        self._player.onStart()
        while True:
            sleep(0.1)
            self._world.update()
            self._eventmanager.runonce()

