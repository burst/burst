#!/usr/bin/python

# TODO: Someone please refactor this long-winded, repetitive, redundant explanation.
'''
The first thing that happens when the eventmanager starts managing a player is, it calls its onStart method.
A player that inherits from Player may choose to override onStart. If it has, it may still call Player's onStart with super().
Player (the class) has the following behaviour in its onStart - it makes the robot accept configuration through its bumpers, then,
as soon as the chest button is pressed, the configuration is locked-in, and the robot moves on to its enterGame method.
Now, if one doesn't wish for this behaviour to take place, one can just override onStart (the way all our players have thus far), and not
call super's onStart. This way, one's robot moves on directly to the player's actual behaviour - which is more convenient for testing purposes.
When one wishes to make a player into a game-worthy player - the kind that is subject to configuration prior to entering the game - all one
has to do is rename one's onStart to enterGame, et voila.
'''

from events import *
from burst.debug_flags import player_py_debug as debug
import burst_consts


class Player(object):

    def __init__(self, world, eventmanager, actions):
        self._world = world
        self._eventmanager = eventmanager
        self._actions = actions
        self._eventsToCallbacksMapping = {}
        self._eventmanager.register(self.onFallenDown, EVENT_FALLEN_DOWN)
        self._eventmanager.register(self.onOnBelly, EVENT_ON_BELLY)
        self._eventmanager.register(self.onOnBack, EVENT_ON_BACK)
        self._eventmanager.register(self._announceSeeingBall, EVENT_BALL_SEEN)
        self._eventmanager.register(self._announceNotSeeingBall, EVENT_BALL_LOST)

    def _register(self, callback, event):
        self._eventsToCallbacksMapping[event] = callback
        self._eventmanager.register(callback, event)

    def _unregister(self, callback=None, event=None):
        if callback != None and event != None:
            self._eventmanager.unregister(callback, event)
            del self._eventsToCallbackMapping[event]
        elif callback == None and event != None:
            self._eventmanager.unregister(self._eventsToCallbackMapping[event], event)
            del self._eventsToCallbackMapping[event]
        elif event == None and callback != None:
            for ev in self._eventsToCallbackMapping:
                if self._eventsToCallbackMapping[ev] == callback:
                    self._eventmanager.unregister(self._eventsToCallbackMapping[ev], ev)
                    del self._eventsToCallbackMapping[ev]

    def _clearAllRegistrations(self):
        for event in self._eventsToCallbacksMapping:
            self._eventsToCallbacksMapping.remove(self._eventsToCallbacksMapping[event], event)
        self._eventsToCallbacksMapping.clear()

    def onStart(self):
        self._world._sentinel.enableDefaultActionSimpleClick(False)
        self._announceNotSeeingBall()
        self._announceSeeingNoGoal()
        self.onInitial()

    def onStop(self): # TODO: Shouldn't this be called onPaused, while onStop deals with the end of the game?
        """ implemented by inheritor from Player. Called whenever player
        moves from action to no action. (game controller moves from playing
        state to another, or when changing behaviors)

        Needs to take care of cleaning up: stop any action you were in the middle of,
        i.e. clearFootsteps.
        """
        self._actions.clearFootsteps()
        self._world._sentinel.enableDefaultActionSimpleClick(True)
        # TODO: initPoseAndRelax?

    def onInitial(self):
        if debug:
            self._actions.say("Entering Initial-Game-State.")
        self._eventmanager.register(self._onLeftBumperPressed, EVENT_LEFT_BUMPER_PRESSED)
        self._eventmanager.register(self._onRightBumperPressed, EVENT_RIGHT_BUMPER_PRESSED)
        self._eventmanager.register(self._onChestButtonPressed, EVENT_CHEST_BUTTON_PRESSED)

    def onLeavingInitial(self):
        pass

    def onConfigured(self):
        self._world.gameStatus.reset() # TODO: Reconsider.
        self._enterGame()

    '''
    def onPlay(self):
        pass

    def onReady(self):
        pass

    def onSet(self):
        pass

    def onPenalized(self):
        pass
    '''

    def onFallenDown(self):
        print "I'm down!"
        self._eventmanager.unregister(self.onFallenDown)

    def onOnBack(self):
        print "I'm on my back."
        self._eventmanager.unregister(self.onOnBack)
        self._actions.executeGettingUpBack().onDone(self.onGottenUpFromBack)
    
    def onGottenUpFromBack(self):
        print "Getting up done (from back)"
        self._eventmanager.register(self.onOnBack, EVENT_ON_BACK)

    def onOnBelly(self):
        print "I'm on my belly."
        self._eventmanager.unregister(self.onOnBelly)
        self._actions.executeGettingUpBelly().onDone(self.onGottenUpFromBelly)
        
    def onGottenUpFromBelly(self):
        print "Getting up done (from belly)"
        self._eventmanager.register(self.onOnBelly, EVENT_ON_BELLY)

    def _announceSeeingBall(self):
        self._world.robot.leds.rightEyeLED.turnOn(burst_consts.RED)

    def _announceNotSeeingBall(self):
        self._world.robot.leds.rightEyeLED.turnOn(burst_consts.BLUE)

    def _announceSeeingBlueGoal(self):
        self._world.robot.leds.rightEyeLED.turnOn(burst_consts.LIGHT_BLUE)

    def _announceSeeingYellowGoal(self):
        self._world.robot.leds.rightEyeLED.turnOn(burst_consts.YELLOW)

    def _announceSeeingNoGoal(self):
        self._world.robot.leds.rightEyeLED.turnOn(burst_consts.OFF)

    def _onLeftBumperPressed(self):
        self._world.playerSettings.toggleteamColor()
        if debug:
            print "Team number: %d. Player number: %d." % (self._world.playerSettings.teamColor, self._world.playerSettings.playerNumber)

    def _onRightBumperPressed(self):
        self._world.playerSettings.togglePlayerNumber()
        if debug:
            print "Team number: %d. Player number: %d." % (self._world.playerSettings.teamColor, self._world.playerSettings.playerNumber)

    def _onChestButtonPressed(self):
        if debug:
            self._actions.say("Configured.")
            print "Team number: %d. Player number: %d." % (self._world.playerSettings.teamColor, self._world.playerSettings.playerNumber)
        for callback in [self._onLeftBumperPressed, self._onRightBumperPressed, self._onChestButtonPressed]:
            self._eventmanager.unregister(callback)
        self.onConfigured()

    def _enterGame(self):
        self.enterGame()

    #############
    # Utilities #
    #############

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
            self._eventmanager.register(f, f.event)


if __name__ == '__main__':
    print "Welcome to the player module's testing procedure. Have fun."
    from eventmanager import MainLoop
    mainloop = MainLoop(GameControllerTester)
    mainloop.run()

