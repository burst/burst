#!/usr/bin/python

# TODO: Someone please refactor this long-winded, repetitive, redundant explanation.
'''
The player module implements the Player class, which all players including Goalie and Kicker
inherit from.

Player implements all the basic robocup player behavior, which means it handles the GameController
states, including Initial, Set, Ready, Play, Finish and Penalized. The main crux of the specific
player, be it a kicker or goalie (or any test player) is done in the main_behavior instance
which is created from the main_behavior_class (or factory) given.

'''

import logging

from twisted.python import log

from burst_events import *
import burst
import burst.moves.poses as poses
import burst_consts
from burst_util import DeferredList
from burst_consts import (InitialRobotState,
    PenalizedRobotState, PlayRobotState, SetRobotState,
    ReadyRobotState,
    InitialGameState, ReadyGameState, FinishGameState,
    SetGameState, PlayGameState, FinishGameState,
    UNKNOWN_GAME_STATE, gameStateToString,
    team_to_defending_goal_color)

from burst.actions.approacher import ApproachXYHActiveLocalization

################################################################################
logger = logging.getLogger("player")
info = logger.info
################################################################################

def overrideme(f):
    return f

def override_with_super(f):
    return f

class Player(object):

    def __init__(self, actions, main_behavior_class):
        """ You may want to override this to set your own
        initial_pose.
        """
        self._world = actions._world
        self._eventmanager = actions._eventmanager
        self._actions = actions
        self._eventsToCallbacksMapping = {}
        self.verbose = burst.options.verbose_player
        # Fall-handling:
        self.registerFallHandling()

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
        self._main_behavior = main_behavior_class(actions) # doesn't start here

    def registerFallHandling(self):
        self._eventmanager.register(self.onOnBelly, EVENT_ON_BELLY)
        self._eventmanager.register(self.onOnBack, EVENT_ON_BACK)
        self._eventmanager.register(self.onPickedUp, EVENT_PICKED_UP)
        self._eventmanager.register(self.onBackOnFeet, EVENT_BACK_ON_FEET)
        self._eventmanager.register(self.onRightSide, EVENT_ON_RIGHT_SIDE)
        self._eventmanager.register(self.onLeftSide, EVENT_ON_LEFT_SIDE)

    def unregisterFallHandling(self):
        self._eventmanager.unregister(self.onOnBelly, EVENT_ON_BELLY)
        self._eventmanager.unregister(self.onOnBack, EVENT_ON_BACK)
        self._eventmanager.unregister(self.onPickedUp, EVENT_PICKED_UP)
        self._eventmanager.unregister(self.onBackOnFeet, EVENT_BACK_ON_FEET)
        self._eventmanager.unregister(self.onRightSide, EVENT_ON_RIGHT_SIDE)
        self._eventmanager.unregister(self.onLeftSide, EVENT_ON_LEFT_SIDE)

    def _register(self, callback, event):
        # TODO - not clear why this is here, should __init__ use it as well.
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

    def onStart(self):
        """ this is called by event manager. does all initial registrations:
        handle all gamecontroller events
        handle fall down events
        setup led changers - video debug and team color and kickoff presentation (TODO kickoff)
        """
        self._world._sentinel.enableDefaultActionSimpleClick(False)
        self._eventmanager.register(self._onChestButtonPressed, EVENT_CHEST_BUTTON_PRESSED)
        Player._announceNotSeeingBall(self)
        Player._announceSeeingNoGoal(self)
        Player._initAsUnconfigured(self)

    #####

    def _initAsUnconfigured(self):
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
        game_state = self._world.gameStatus.gameState
        if self.verbose:
            self._actions.say("Player: Unconfigured: Game state = %s" % game_state)
        # Explanation:
        #  if unknown state:
        #   then just start playing (shortcut to _onConfigured)
        #  else:
        #   wait for either chest button or game state change
        #    when that happens call self._onConfigured
        if burst.options.test_configure:
            info("NOTICE: testing configure with buttons - ignoring game controller.")
            return
        if not burst_consts.ALWAYS_CONFIGURE and game_state is UNKNOWN_GAME_STATE:
            info("NOTICE: No game controller and ALWAYS_CONFIGURE is False - going straight to %s" % (
                'Ready' if burst.options.test_ready else 'Playing'))
            info("NOTICE: PLEASE FIX BEFORE GAME")
            self._onConfigured()
            if burst.options.test_ready:
                def onReadyDone():
                    info("testing Ready: Done with Ready")
                self._onReady().onDone(onReadyDone)
            else:
                self._startMainBehavior()
        else:
            info("Player: waiting for configuration event (change in game state, or chest button)")
            self._eventmanager.firstEventDeferred(EVENT_GAME_STATE_CHANGED,
                EVENT_CHEST_BUTTON_PRESSED).addCallback(self._onConfigured).addErrback(log.err)

    def _startMainBehavior(self):
        print "="*80
        print "= %s =" % (('starting %s' % self._main_behavior.name).center(76))
        print "="*80
        self._main_behavior.start()
        return self._main_behavior

    def _onConfigured(self, result=None):
        """ we get here when done configuring """
        self._configuring = False
        if self.verbose:
            self._actions.say('Configured')
        settings = self._world.playerSettings
        state = self._world.gameStatus.gameState
        print "Team number %d, Team color %d, Player number %d, game state %s" % (
            settings.teamNumber, settings.teamColor, settings.playerNumber,
            gameStateToString(state))
        for callback in [self._onLeftBumperPressed, self._onRightBumperPressed]:
            self._eventmanager.unregister(callback)
        self._world.gameStatus.reset() # TODO: Reconsider.
        self._world.configure(our_color=team_to_defending_goal_color(self._world.robot.team_color))
        # register for future changes
        self._eventmanager.register(self._onNewGameState, EVENT_GAME_STATE_CHANGED)

    def _onNewGameState(self):
        """ we only register here after we have actually been configured - simplifies the logic """
        state = self._world.gameStatus.gameState
        if self.verbose:
            info("Player: entered %s Game State" % gameStateToString(state))
        {InitialGameState   :self._onInitial,
         SetGameState       :self._onSet,
         ReadyGameState     :self._onReady,
         PlayGameState      :self._onPlay,
         FinishGameState    :self._onFinish,
         UNKNOWN_GAME_STATE :self._onPlay}[state]()

    def _onFinish(self):
        self.onStop() # TODO - can this be called twice right now, from a ctrl-c / eventmanager.quit and from FinishGameState?

    def _onPlay(self):
        info("Player: OnPlay")
        self._startMainBehavior()
        self._main_behavior.onDone(self._onMainBehaviorDone)

    def _onMainBehaviorDone(self):
        info("Player: Main Behavior is done (%s)" % (self._main_behavior))

    def _onSet(self):
        info("Player: On Set: TODO")
        self._main_behavior.stop()

    def _onReady(self):
        self._main_behavior.stop()
        gameStatus = self._world.gameStatus
        weAreKickTeam = gameStatus.mySettings.teamColor == gameStatus.kickOffTeam
        jersey = self._world.robot.jersey
        x, y = burst_consts.READY_INITIAL_LOCATIONS[weAreKickTeam][jersey][burst_consts.INITIAL_POSITION] # XXX - no idea what that last dict is good for, contains one item right now.
        info("onReady: #%d going to %2.1f, %2.1f" % (jersey, x, y))
        self._approacher = ApproachXYHActiveLocalization(self._actions, x, y, 0.0) # heading towards opposing goal
        self._approacher.start()
        self._approacher.onDone(self._onReadyDone)
        return self._approacher

    def _onReadyDone(self):
        info("INFO: Player: #%s Reached Ready Position!" % (self._world.robot.jersey))

    def _onInitial(self):
        info("Player: On Initial")
        self._main_behavior.stop()

    def onStop(self):
        """ Called when we want to shutdown our program - i.e. game over, go home, or whatever.
        Not called during the game (unless we have a bug! do we? nah..)

        Needs to take care of cleaning up: stop any action you were in the middle of,
        i.e. clearFootsteps.
        """
        def afterBehaviorStopped():
            self._actions.clearFootsteps()
            self._actions.killAll()
            self._world._sentinel.enableDefaultActionSimpleClick(True)
            self._world.robot.leds.turnEverythingOff()
            self._world.robot.leds.rightEarLED.turnOn()
            self._world.robot.leds.leftEarLED.turnOn()
        self._main_behavior.stop().onDone(afterBehaviorStopped)

    def onPickedUp(self):
        self._actions.say("I'm being picked-up")
        #self._eventmanager.unregister(self.onPickedUp, EVENT_PICKED_UP)

    def onBackOnFeet(self):
        self._actions.say("I'm back on my feet")
        self.registerFallHandling()

    def onOnBack(self):
        self._actions.say("I'm on my back.")
#        print "Player: onOnBack: stopping main_behavior"
#        self._actions.killAll()
#        self._main_behavior.stop()
#        self.unregisterFallHandling()
#        self._actions.executeGettingUpBack().onDone(self.onGottenUpFromBack)

    def onOnBelly(self):
        self._actions.say("I'm on my belly.")
#        print "Player: onOnBelly: stopping main_behavior"
#        self._actions.killAll()
#        self._main_behavior.stop()
#        self.unregisterFallHandling()
#        self._actions.executeGettingUpBelly().onDone(self.onGottenUpFromBelly)

    def onGottenUpFromBack(self):
        self._actions.say("Getting up done (from back)")
        self.registerFallHandling()

        info("Player: onGottenUpFromBack")
        self._main_behavior.start().onDone(self._onMainBehaviorDone)

    def onGottenUpFromBelly(self):
        self._actions.say("Getting up done (from belly)")
        self.registerFallHandling()

        info("Player: onGottenUpFromBelly")
        self._main_behavior.start().onDone(self._onMainBehaviorDone)

    def onRightSide(self):
        self._actions.say("I'm on the right side")
        #self.unregisterFallHandling()
        #self._actions.executeGettingUpBelly().onDone(self.onGottenUpFromBelly)

    def onLeftSide(self):
        self._actions.say("I'm on the left side")
        #self.unregisterFallHandling()
        #self._actions.executeGettingUpBelly().onDone(self.onGottenUpFromBelly)

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
            info("Team color: %d" % (self._world.playerSettings.teamColor))

    def _onRightBumperPressed(self):
#        self._actions.say("hello. don't worry, be happy!")
        info(str(self))

    def _onChestButtonPressed(self):
        """ This callback is registered only after start - when
        the chest button has been pressed we stop being in the configure
        state, and call onConfigured
        """
        info("Player: onChestButtonPressed")
        if self._configuring: return # 

        self._world.gameStatus.getMyPlayerStatus().onChestButtonPressed()
        info("Penalized After  = %s, %s" % (self._world.robot.penalized, self._world.gameStatus.getMyPlayerStatus()))

        # TODO - penalize me, also make sure that if I am penalized from chest
        # then I remain so until either I am unpenalized from chest, OR the game
        # state changes to Penalized (for me), and THEN Unpenalized from game state.

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

