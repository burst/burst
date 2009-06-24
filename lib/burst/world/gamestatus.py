#!/usr/bin/python


__all__ = ['GameStatus', 'EmptyGameStatus']

import logging

import burst
from burst_consts import GAME_CONTROLLER_NUM_PLAYERS, GAME_CONTROLLER_NUM_TEAMS
import burst_events
from burst_events import EVENT_GAME_STATE_CHANGED
import gamecontroller
from gamecontroller import constants as constants
from gamecontroller_consts import *
from burst.world.robot import LEDs
import burst_consts

################################################################################
logger = logging.getLogger('gamestatus')
info = logger.info
################################################################################

class PlayerStatus(object):
    '''
    Keeps track of the status of a single player.
    '''
    def __init__(self, teamColor, playerNumber):
        self.config(teamColor, playerNumber)
        self.status = UNKNOWN_PLAYER_STATUS
        self.penalized = False # This is the actual penalized state - since
                        # it can be set from two different sources, we need
                        # to keep track of it.
        self._game_state_when_chest_penalized = None

    def config(self, teamColor, playerNumber):
        self.teamColor = teamColor
        self.playerNumber = playerNumber

    def setStatus(self, status, remainingTimeForPenalty):
        self.remainingTimeForPenalty = remainingTimeForPenalty
        if self.status is status:
            return
        self.status = status
        # we become penalized if we were not penalized and the status
        # says we are. ChestButton presses also change this value,
        # so we
        if self._game_state_when_chest_penalized and state == self._game_state_when_chest_penalized:
            # game controller state remains as it was when the chest button was pressed - we
            # will just ignore it
            return
        if self.penalized:
            info("Moving from penalized to not from gamestate")
        # back to gamecontroller-control
        self._game_state_when_chest_penalized = None
        self.penalized = self.stateIsPenalized()

    def onChestButtonPressed(self):
        self.penalized = not self.penalized
        self._game_state_when_chest_penalized = self.status

    def stateIsPenalized(self):
        return self.status in constants.Penalties

    def isPenalized(self):
        return self.penalized

    def __str__(self):
        return '<PlayerStatus %s %s %s>' % ((self.penalized and 'T') or 'F',
            (self.stateIsPenalized() and 'T') or 'F', self.status if str(self.status).isdigit() else 'no gc')


class GameStatus(object):
    '''
    Each robot will host one instance of this class. It will be in charge of tracking the state of the game - who is penalized, what state
    the game is in (ready/set/play...), what the score is, etc. It will fire the appropriate events.
    '''

    def __init__(self, world, playerSettings):
        self.verbose = burst.options.verbose_gamestatus
        self.world = world # TODO: Right now, I only need this for the LEDs. Pass them instead?
        self.mySettings = playerSettings
        self.players = [[PlayerStatus(teamColor, playerNumber)
            for playerNumber in xrange(GAME_CONTROLLER_NUM_PLAYERS)]
                            for teamColor in xrange(GAME_CONTROLLER_NUM_TEAMS)]
        self.newEvents = set()
        self.gameState = UNKNOWN_GAME_STATE
        self.reset()
        self.setColors()

    def reset(self):
        if self.verbose:
            info("GameStatus: reseting")
        self.firstMessageReceived = False
        self.myTeamScore = -1 # Signal that it is unknown, as long as no message has been received from the game controller.
        self.opposingTeamScore = -1 # Signal that it is unknown, as long as no message has been received from the game controller.
        self.kickOffTeam = 1 - self.mySettings.teamColor # TODO: Not set through the legs?

    def _isMe(self, player):
        return player.teamColor == self.mySettings.teamColor and player.playerNumber == self.mySettings.playerNumber

    def readMessage(self, message):
        if not self.firstMessageReceived:
            self.firstMessageReceived = True
            self._recordMessage(message)
            self._fireInitialEvents()
        else:
            self._readNewMessage(message)
        self.setColors()

    def _recordMessage(self, message):
        '''
        Commit the message to memory. Make sure you calculate the events first, since this, of course, overrides your previous memories,
        and prevents you from calculating events based on the difference between the new message and those aforementioned previous memories.
        '''
        self.gameState = message.getGameState()
        self.kickOffTeam = message.getKickOffTeamNumber()
        self.myTeamScore = message.getTeamScore(self.mySettings.teamColor)
        self.opposingTeamScore = message.getTeamScore(1 - self.mySettings.teamColor)
        for team in xrange(GAME_CONTROLLER_NUM_TEAMS):
            for player in xrange(GAME_CONTROLLER_NUM_PLAYERS):
                self.players[team][player].setStatus(message.getPenaltyStatus(team, player), message.getPenaltyTimeRemaining(team, player))

    def _readNewMessage(self, message):
        '''
        When a new message is received (and not for the first time!), events are calculated based on the difference between the memory
        we have of the previous message. Then, the memory of the new message overrides the memory of the old one.
        '''
        # TODO: Currently, only calculating the interesting events.
        # Calculate events based on the difference between this message and the one before it:
        self._calcGoalRelatedEvents(message)
        self._calcGameStateRelatedEvents(message)
        self._calcPenaltyRelatedEvents(message)
        # The next time around, the present is the past and the future is the present.
        self._recordMessage(message)

    def _calcGoalRelatedEvents(self, message):
        '''
        Calculates events that are related to goals: either team having perhaps scored a goal.
        '''
        if self.myTeamScore < message.getTeamScore(self.mySettings.teamColor):
            self.newEvents.add(burst_events.EVENT_GOAL_SCORED_BY_MY_TEAM)
            self.newEvents.add(burst_events.EVENT_GOAL_SCORED)
        if self.opposingTeamScore < message.getTeamScore(1 - self.mySettings.teamColor):
            self.newEvents.add(burst_events.EVENT_GOAL_SCORED_BY_OPPOSING_TEAM)
            self.newEvents.add(burst_events.EVENT_GOAL_SCORED)

    def _calcGameStateRelatedEvents(self, message):
        '''
        Calculates events that are related to the game state changing: the leaving of one game state, and the transition to a new one.
        '''
        if self.gameState != message.getGameState():
            self.newEvents.add(gamestate_to_from_event[self.gameState])
            self.newEvents.add(gamestate_to_to_event[message.getGameState()])
            self.newEvents.add(EVENT_GAME_STATE_CHANGED)

    def _calcPenaltyRelatedEvents(self, message): # TODO: Rename.
        '''
        Calculates events that are related to a player's status (not necessarily one's own) being changed. Penalties, etc.
        '''
        for teamColor in xrange(GAME_CONTROLLER_NUM_TEAMS):
            for playerNumber in xrange(GAME_CONTROLLER_NUM_PLAYERS):
                player = self.players[teamColor][playerNumber]
                # If something's changed:
                if player.status != message.getPenaltyStatus(teamColor, playerNumber):
                    # If switching to a penalty status:
                    if message.getPenaltyStatus(teamColor, playerNumber) in constants.Penalties and not player.status in constants.Penalties:
                        if player.teamColor == self.mySettings.teamColor:
                            if player.playerNumber == self.mySettings.playerNumber:
                                self.newEvents.add(burst_events.EVENT_I_GOT_PENALIZED)
                            else:
                                self.newEvents.add(burst_events.EVENT_TEAMMATE_PENALIZED)
                        else:
                            self.newEvents.add(burst_events.EVENT_OPPONENT_PENALIZED)
                    # If returning from a penalty status:
                    if player.status in constants.Penalties and not message.getPenaltyStatus(teamColor, playerNumber) in constants.Penalties:
                        if player.teamColor == self.mySettings.teamColor:
                            if player.playerNumber == self.mySettings.playerNumber:
                                self.newEvents.add(burst_events.EVENT_I_GOT_UNPENALIZED)
                            else:
                                self.newEvents.add(burst_events.EVENT_TEAMMATE_UNPENALIZED)
                        else:
                            self.newEvents.add(burst_events.EVENT_OPPONENT_UNPENALIZED)

    def _fireInitialEvents(self): # TODO: We'd might like to have the events fired in some predetermined order.
        for state in ['Initial', 'Ready', 'Set', 'Play', 'Finish']:
            if self.gameState == getattr(constants, state+'GameState'):
                self.newEvents.add(getattr(burst_events, 'EVENT_SWITCHED_TO_'+state.upper()+'_GAME_STATE'))
                self.newEvents.add(EVENT_GAME_STATE_CHANGED)
                break
        if self.players[self.mySettings.teamColor][self.mySettings.playerNumber].isPenalized():
            self.newEvents.add(burst_events.EVENT_I_GOT_PENALIZED)

    def calc_events(self, events, deferreds):
#        print self.mySettings.playerNumber
        # Add any event you have inferred from the last message you got from the game controller.
        for event in self.newEvents:
            events.add(event)
        # Don't refire these events unless they recur.
        self.newEvents.clear()

    def getScore(self, teamColor):
        if teamColor == self.mySettings.teamColor:
            return self.myTeamScore
        else:
            return self.opposingTeamScore

    def getMyPlayerStatus(self):
        # TODO - whaaa? why do I need to iterate this everytime, isn't it enough to "onPlayerNumberChanged"
        # and "onTeamColorChanged"? do those every happen? don't we set them at configuration time (through
        # leg buttons) only?
        for teamColor in xrange(GAME_CONTROLLER_NUM_TEAMS):
            for playerNumber in xrange(GAME_CONTROLLER_NUM_PLAYERS):
                if self._isMe(self.players[teamColor][playerNumber]):
                    return self.players[teamColor][playerNumber]
        raise Exception("getMyPlayerStatus() - can't find myself among the players.")

    def changeKickOffTeam(self, kickOffTeam): # TODO: Untested.
        # TODO: I've been led to believe Python has properties/attributes/whatever, like C#. I probably just want to use that instead for the
        # kickOffTeam variable, so that setColors() is called whenever it's changed.
        raise Exception("This feature has not yet been tested. It should work, but do test it before removing this line.")
        self.kickOffTeam = kickOffTeam
        self.setColors()

    def myRobotState(self): # TODO: ConfigurationRobotState?
        if self.getMyPlayerStatus().isPenalized():
            return PenalizedRobotState
        else:
            return GameStateToRobotStateMap[self.gameState]

    def setColors(self):
        ''' Update the LEDs according to the information you carry. '''
        self.world.robot.leds.rightFootLED.turnOn(burst_consts.TeamColors[self.kickOffTeam]) # TODO: constants/burst_constants
        self.world.robot.leds.chestButtonLED.turnOn(constants.robotStateToChestButtonColor[self.myRobotState()])


if __name__ == '__main__':
    welcome = "Testing the gamestatus module."
    print len(welcome)*"*" + "\n" + welcome + "\n" + len(welcome)*"*"
    print "No tests have been implemented, thus far."

