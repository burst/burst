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

