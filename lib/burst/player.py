#!/usr/bin/python


from events import *
from burst.debug_flags import player_py_debug as debug
import burst_consts


class Player(object):

    def __init__(self, world, eventmanager, actions):
        self._world = world
        self._eventmanager = eventmanager
        self._actions = actions
        self._eventmanager.register(self.onFallenDown, EVENT_FALLEN_DOWN)
        self._eventmanager.register(self.onOnBelly, EVENT_ON_BELLY)
        self._eventmanager.register(self.onOnBack, EVENT_ON_BACK)
        self._eventmanager.register(self._announceSeeingBall, EVENT_BALL_SEEN)
        self._eventmanager.register(self._announceNotSeeingBall, EVENT_BALL_LOST)
    
    def onGCPlaying(self):
        """ only state player needs to deal with, the rest are done
        by the events object """
        self.onStart()

    def onStart(self):
        self._announceNotSeeingBall()
        self._announceSeeingNoGoal()
        self.onInitial()

    def onStop(self):
        """ implemented by inheritor from Player. Called whenever player
        moves from action to no action. (game controller moves from playing
        state to another, or when changing behaviors)

        Needs to take care of cleaning up: stop any action you were in the middle of,
        i.e. clearFootsteps.
        """
        self._actions.clearFootsteps()

    def onInitial(self):
        if debug:
#            self._actions.say("ENTERING INITIAL")
            print "Entering Initial"
        def onLeftBumperPressed(self=self):
            self._world.playerSettings.toggleteamColor()
            if debug:
                print "Team number: %d. Player number: %d." % (self._world.playerSettings.teamColor, self._world.playerSettings.playerNumber)
        def onRightBumperPressed(self=self):
            self._world.playerSettings.togglePlayerNumber()
            if debug:
                print "Team number: %d. Player number: %d." % (self._world.playerSettings.teamColor, self._world.playerSettings.playerNumber)
            print "Team number: %d. Player number: %d." % (self._world.playerSettings.teamColor, self._world.playerSettings.playerNumber)
        def onChestButtonPressed(self=self):
            self._world.gameStatus.reset()
            if debug:
                self._actions.say("LEAVING INITIAL")
                print "Team number: %d. Player number: %d." % (self._world.playerSettings.teamColor, self._world.playerSettings.playerNumber)
            for callback in [onLeftBumperPressed, onRightBumperPressed, onChestButtonPressed]:
                self._eventmanager.unregister(callback)
            self.onConfigured()
        self._eventmanager.register(onLeftBumperPressed, EVENT_LEFT_BUMPER_PRESSED)
        self._eventmanager.register(onRightBumperPressed, EVENT_RIGHT_BUMPER_PRESSED)
        self._eventmanager.register(onChestButtonPressed, EVENT_CHEST_BUTTON_PRESSED)

    def onLeavingInitial(self):
        pass

    def onConfigured(self):
        pass # TODO: Go to the state that's associated with the current GameState.

    def onPlay(self):
        pass

    def onReady(self):
        pass

    def onSet(self):
        pass

    def onPenalized(self):
        pass

    def onFallenDown(self):
        print "I'm down!"
        self._eventmanager.unregister(self.onFallenDown)

    def onOnBack(self):
        print "I'm on my back."
        self._eventmanager.unregister(self.onOnBack)
        # temporarily removed
        #self._actions.executeGettingUpBack().onDone(self.gettingUpDoneBack)
    
    def gettingUpDoneBack(self):
        print "Getting up done!"
        self._eventmanager.register(self.onOnBack, EVENT_ON_BACK)

    def onOnBelly(self):
        print "I'm on my belly."
        self._eventmanager.unregister(self.onOnBelly)
        # temporarily removed
        #self._actions.executeGettingUpBelly().onDone(self.gettingUpDoneBelly)
        
    def gettingUpDoneBelly(self):
        print "Getting up done!"
        self._eventmanager.register(self.onOnBelly, EVENT_ON_BELLY)

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
            self._eventmanager.register(f, f.event)

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

if __name__ == '__main__':
    print "Welcome to the player module's testing procedure. Have fun."
    from eventmanager import MainLoop
    mainloop = MainLoop(GameControllerTester)
    mainloop.run()

