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
        print "I'm down!"
        self._eventmanager.unregister(EVENT_FALLEN_DOWN)

    def onOnBack(self):
        print "I'm on my back."
        self._eventmanager.unregister(EVENT_ON_BACK)
        # temporarily removed
        #self._actions.executeGettingUpBack().onDone(self.gettingUpDoneBack)
    
    def gettingUpDoneBack(self):
        print "Getting up done!"
        self._eventmanager.register(EVENT_ON_BACK, self.onOnBack)

    def onOnBelly(self):
        print "I'm on my belly."
        self._eventmanager.unregister(EVENT_ON_BELLY)
        # temporarily removed
        #self._actions.executeGettingUpBelly().onDone(self.gettingUpDoneBelly)
        
    def gettingUpDoneBelly(self):
        print "Getting up done!"
        self._eventmanager.register(EVENT_ON_BELLY, self.onOnBelly)

    # Utilities

    def registerDecoratedEventHandlers(self):
        """
        Intended usage: if you have a clear method -> event in your player, you can
        mark each such method with the event it handles like so:
        @eventhandler(EVENT_YGRP_POSITION_CHANGED)
        def my_method(self):
            ...

        You will then have access to self.my_method.event as the event you gave,
        and this utility method uses that to register all of those events without
        having to redclare the event name -> method pairing.
        """
        # register to events - see singletime
        for fname in [fname for fname in dir(self) if hasattr(getattr(self, fname), 'event')]:
            f = getattr(self, fname)
            self._eventmanager.register(f.event, f)


