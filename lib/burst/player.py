#!/usr/bin/python

# TODO: Someone please refactor this long-winded, repetitive, redundant explanation.
'''
The player module implements the Player class, which all players including Goalie and Kicker
inherit from.

Player implements all the common behavior, including gamecontroller handling and fall
handling, with suitable places for higher level behavior to take over.

Callbacks that Inheritor needs to reimplement:
 enterGame - called when PLAYING state is achieved.
 onStop  - called right before shutdown of process, to let Player clean things up.
           implemented in Player and can be overridden (again, remember to super).

Other callbacks that are more like implementation details but might be important:

 onPlaying will call enterGame. This is the real main for users.

 onStart - when the player has been constructed. Not meant to be used
           during the game except by the Player class itself.
 onConfigured - called by _onChestButtonPressed. when called it means the
            robot stopps checking for bumper button or changes to kick off team (TODO
            the later), will check current broadcast state, enter it (exactly as if
            it was there to begin with), and register to all other state changes.
'''

from events import *
import burst
import burst.moves.poses as poses
import burst_consts
from burst_consts import (InitialRobotState,
    PenalizedRobotState, PlayRobotState, SetRobotState,
    ReadyRobotState,
    InitialGameState, ReadyGameState, FinishGameState,
    SetGameState, PlayGameState, FinishGameState,
    UNKNOWN_GAME_STATE, gameStateToString)

def overrideme(f):
    return f

class Player(object):

    def __init__(self, world, eventmanager, actions, initial_pose=poses.INITIAL_POS):
        """ You may want to override this to set your own
        initial_pose.
        """
        self._world = world
        self._eventmanager = eventmanager
        self._actions = actions
        self._eventsToCallbacksMapping = {}
        self.verbose = burst.options.verbose_player
        # Fall-handling:
        self._eventmanager.register(self.onFallenDown, EVENT_FALLEN_DOWN)
        self._eventmanager.register(self.onOnBelly, EVENT_ON_BELLY)
        self._eventmanager.register(self.onOnBack, EVENT_ON_BACK)
        # Debugging aids via the LEDs:
        ### Ball:
        self._world.robot.leds.rightEarLED.turnOn()
        self._world.robot.leds.leftEarLED.turnOn()
        self._announceNotSeeingBall()
        self._eventmanager.register(self._announceSeeingBall, EVENT_BALL_SEEN)
        self._eventmanager.register(self._announceNotSeeingBall, EVENT_BALL_LOST)
        ### Goals:
        self._seeingAllBlueGoal = False
        self._seeingAllYellowGoal = False
        self._announceSeeingNoGoal()
        self._eventmanager.register(self._announceSeeingYellowGoal, EVENT_ALL_YELLOW_GOAL_SEEN)
        self._eventmanager.register(self._announceSeeingBlueGoal, EVENT_ALL_BLUE_GOAL_SEEN)
        self._eventmanager.register(self._announceSeeingNoGoal, EVENT_ALL_YELLOW_GOAL_LOST)
        self._eventmanager.register(self._announceSeeingNoGoal, EVENT_ALL_BLUE_GOAL_LOST)
        self._initial_pose = initial_pose

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
        for event, callback in self._eventsToCallbacksMapping.items():
            self._eventsToCallbacksMapping.remove(callback, event)
        self._eventsToCallbacksMapping.clear()

    # Start game callbacks

    @overrideme
    def onStart(self):
        """ this is called by event manager. does all initial registrations:
        handle all gamecontroller events
        handle fall down events
        setup led changers - video debug and team color and kickoff presentation (TODO kickoff)
        """
        self._world._sentinel.enableDefaultActionSimpleClick(False)
        Player._announceNotSeeingBall(self)
        Player._announceSeeingNoGoal(self)
        Player._onYetUnknownGameState(self)

    #####

    def _onYetUnknownGameState(self):
        """ This is called when we want to configure the robot. We have just been turned
        on, but the game can be in any of several states:
         * no game controller running (tests)
         * Initial state
         * any other state
        we allow configuration from buttons in this state, and we exit this state either by
        a chest button click (then we move to penalized), or by a gamecontroller state
        change.
        """
        self._configuring = True
        # Buttons:
        self._eventmanager.register(self._onLeftBumperPressed, EVENT_LEFT_BUMPER_PRESSED)
        self._eventmanager.register(self._onRightBumperPressed, EVENT_RIGHT_BUMPER_PRESSED)
        self._eventmanager.register(self._onChestButtonPressed, EVENT_CHEST_BUTTON_PRESSED)
        # Game Controller:
        self._eventmanager.register_oneshot(self._waitForKnownGameState, EVENT_GAME_STATE_CHANGED)
        if self.verbose:
            self._actions.say("Unconfigured")

    def _waitForKnownGameState(self):
        game_state = self._world.gameStatus.gameState
        if game_state is UNKNOWN_GAME_STATE:
            self._eventmanager.register_oneshot(self._waitForKnownGameState,
                    EVENT_GAME_STATE_CHANGED)
        elif self._configuring:
            if game_state is InitialGameState:
                if self.verbose:
                    print "Player: saw Initial game state, unconfigured"
                self._eventmanager.register_oneshot(self._onExpectingConfigureGameStateChange,
                    EVENT_GAME_STATE_CHANGED) # TODO - use SWITCHED_FROM?
            else:
                if self.verbose:
                    print "Player: Game already in progress, wait for chest button to be configured"

    def _onExpectingConfigureGameStateChange(self):
        """ handle any generic change to game state - should probably use
        specific functions for onPlaying, onReady, onPlay, onPenalized, onFininshed
        """
        if self._world.gameStatus.gameState is InitialGameState:
            if self.verbose:
                print "Player: saw state %s, continue configuration" % self._world.gameStatus.gameState
            self._eventmanager.register_once(self._onExpectingConfigureGameStateChange, EVENT_GAME_STATE_CHANGED)
        else:
            # ok, so either no gamecontroller (UNKNOWN state), or the game is a-foot. But since we are still unconfigured,
            # we will just wait for the chest button
            if self.verbose:
                print "Player: configured through gamecontroller gamestate change"
            self._onConfigured()

    #####

    def _onConfigured(self):
        """ we get here when done configuring """
        self._configuring = False
        if self.verbose:
            self._actions.say('Configured')
        settings = self._world.playerSettings
        state = self._world.gameStatus.gameState
        print "Team number %d, Team color %d, Player number %d, game state %s" % (
            settings.teamNumber, settings.teamColor, settings.playerNumber,
            gameStateToString(state))
        # TODO - set the kickoff position for the robot according to current
        for callback in [self._onLeftBumperPressed, self._onRightBumperPressed,
            self._onChestButtonPressed, self._onExpectingConfigureGameStateChange,
            self._waitForKnownGameState]:
            self._eventmanager.unregister(callback)
        self._world.gameStatus.reset() # TODO: Reconsider.
        self._enterGame()

    def _enterGame(self):
        self.enterGame()

    def enterGame(self):
        self._actions.say("This is the default Player dot enterGame, please override me")

    def onStop(self): # TODO: Shouldn't this be called onPaused, while onStop deals with the end of the game?
        """ implemented by inheritor from Player. Called whenever player
        moves from action to no action. (game controller moves from playing
        state to another, or when changing behaviors)

        Needs to take care of cleaning up: stop any action you were in the middle of,
        i.e. clearFootsteps.
        """
        self._actions.clearFootsteps()
        self._world._sentinel.enableDefaultActionSimpleClick(True)
        self._world.robot.leds.turnEverythingOff()
        self._world.robot.leds.rightEarLED.turnOn()
        self._world.robot.leds.leftEarLED.turnOn()
        # TODO: initPoseAndRelax?

    def onFallenDown(self):
        print "I'm down!"
        self._eventmanager.unregister(self.onFallenDown)

    def onOnBack(self):
        print "I'm on my back."
        self._eventmanager.unregister(self.onOnBack)
        #self._actions.executeGettingUpBack().onDone(self.onGottenUpFromBack)
    
    def onGottenUpFromBack(self):
        print "Getting up done (from back)"
        self._eventmanager.register(self.onOnBack, EVENT_ON_BACK)

    def onOnBelly(self):
        print "I'm on my belly."
        self._eventmanager.unregister(self.onOnBelly)
        #self._actions.executeGettingUpBelly().onDone(self.onGottenUpFromBelly)
        
    def onGottenUpFromBelly(self):
        print "Getting up done (from belly)"
        self._eventmanager.register(self.onOnBelly, EVENT_ON_BELLY)

    def _announceSeeingBall(self):
        self._world.robot.leds.rightEyeLED.turnOn(burst_consts.RED)

    def _announceNotSeeingBall(self):
        self._world.robot.leds.rightEyeLED.turnOn(burst_consts.BLUE)

    def _announceSeeingBlueGoal(self):
        self._world.robot.leds.leftEyeLED.turnOn(burst_consts.LIGHT_BLUE)

    def _announceSeeingYellowGoal(self):
        self._world.robot.leds.leftEyeLED.turnOn(burst_consts.YELLOW)

    def _announceSeeingNoGoal(self):
        self._world.robot.leds.leftEyeLED.turnOn(burst_consts.OFF)

    def _onLeftBumperPressed(self):
        self._world.playerSettings.toggleteamColor()
        if self.verbose:
            print "Team color: %d" % (self._world.playerSettings.teamColor)

    def _onRightBumperPressed(self):
#        self._actions.say("hello. don't worry, be happy!")
        print "hello. don't worry, be happy!"

    def _onChestButtonPressed(self):
        """ This callback is registered only after start - when
        the chest button has been pressed we stop being in the configure
        state, and call onConfigured
        """
        print "Player: onChestButtonPressed"
        if self._configuring:
            self._onConfigured()
        # TODO - penalize me, also make sure that if I am penalized from chest
        # then I remain so until either I am unpenalized from chest, OR the game
        # state changes to Penalized (for me), and THEN Unpenalized from game state.

    #############
    # Utilities #
    #############

    def log(self, msg):
        print "%s: %s" % (self.__class__.__name__, msg)

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

