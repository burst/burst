from burst.events import *
from events import EVENT_ON_BACK

class Player(object):

    def __init__(self, world, eventmanager, actions):
        self._world = world
        self._eventmanager = eventmanager
        self._actions = actions
        self._eventmanager.register(EVENT_FALLEN_DOWN, self.onFallenDown)
        self._eventmanager.register(EVENT_ON_BELLY, self.onOnBelly)
        self._eventmanager.register(EVENT_ON_BACK, self.onOnBack)
    
    def onGCPlaying(self):
        """ only state player needs to deal with, the rest are done
        by the events object """
        self.onStart()

    def onStart(self):
        """ implemented by inheritor from Player. Called whenever player
        moves from no action to action. (game controller playing or from
        penalized states, or when changing behaviors) """
        raise NotImplementedError("onStart")

    def onStop(self):
        """ implemented by inheritor from Player. Called whenever player
        moves from action to no action. (game controller moves from playing
        state to another, or when changing behaviors)

        Needs to take care of cleaning up: stop any action you were in the middle of,
        i.e. clearFootsteps.
        """
        self._actions.clearFootsteps()

    def onFallenDown(self):
        self._eventmanager.unregister(EVENT_FALLEN_DOWN)
        print "I'm down!"

    def onOnBack(self):
        self._eventmanager.unregister(EVENT_ON_BACK)
        print "I'm on my back."

    def onOnBelly(self):
        self._eventmanager.unregister(EVENT_ON_BELLY)
        print "I'm on my belly."
