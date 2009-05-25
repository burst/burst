#!/usr/bin/python

__all__ = ['GameStatus']


import burst
from burst import events as events
import gamecontroller
from gamecontroller import constants as constants
from gamecontroller.constants import *


# A helper class for storing the status of the different players on the field.
class PlayerStatus(object):

    def __init__(self, teamIdentifier=None, playerNumber=None):
        self.config(teamIdentifier, playerNumber)

    def config(self, teamIdentifier=None, playerNumber=None):
        self.teamIdentifier = teamIdentifier
        self.playerNumber = playerNumber

    def setStatus(self, status, remainingTimeForPenalty):
        self.status = status
        self.remainingTimeForPenalty = remainingTimeForPenalty



class GameStatus(object):

    def __init__(self, mySettings):
        self.mySettings = mySettings
        self.firstMessageReceived = False
        self.players = [[PlayerStatus(j, i+1) for i in xrange(11)] for j in xrange(2)]
        self.newEvents = set()

    def readMessage(self, message):
        if not self.firstMessageReceived:
            self.firstMessageReceived = True
            self._recordMessage(message)
        else:
            self._readNewMessage(message)

    def _recordMessage(self, message):
        if message.getTeamNumber(0) == self.mySettings.teamNumber:
            self.myTeamIdentifier = 0
        elif message.getTeamNumber(1) == self.mySettings.teamNumber:
            self.myTeamIdentifier = 1
        else:
            raise Exception("Couldn't find my team!") # TODO: Should this still be here during the competition?
        self.opposingTeamIdentifier = 1 - self.myTeamIdentifier
        # TODO: Doesn't the team identifier change during half time? If so, unless I change something here, we need to reboot the robots.
        self.gameState = message.getGameState()
        self.kickOffTeam = message.getKickOffTeamNumber()
        self.myTeamScore = message.getTeamScore(self.myTeamIdentifier)
        self.opposingTeamScore = message.getTeamScore(self.opposingTeamIdentifier)
        for team in xrange(2):
            for player in xrange(11):
                self.players[team][player].setStatus(message.getPenaltyStatus(team, player), message.getPenaltyTimeRemaining(team, player))

    def _readNewMessage(self, message):
        # TODO: Currently, only calculating the interesting events.
        # Goals:
        if self.myTeamScore < message.getTeamScore(self.myTeamIdentifier):
            self.newEvents.add(events.EVENT_GOAL_SCORED_BY_MY_TEAM)
        if self.opposingTeamScore < message.getTeamScore(self.opposingTeamIdentifier):
            self.newEvents.add(events.EVENT_GOAL_SCORED_BY_OPPOSING_TEAM)
        if events.EVENT_GOAL_SCORED_BY_MY_TEAM in self.newEvents or events.EVENT_GOAL_SCORED_BY_OPPOSING_TEAM in self.newEvents:
            self.newEvents.add(events.EVENT_GOAL_SCORED)
        # Game-state changes:
        for state in ['Initial', 'Ready', 'Set', 'Play', 'Finish']:
            if self.gameState == getattr(constants, state+'GameState') and message.getGameState() != getattr(constants, state+'GameState'):
                self.newEvents.add(getattr(events, 'EVENT_SWITCHED_FROM_'+state.upper()+'_GAME_STATE'))
            if self.gameState != getattr(constants, state+'GameState') and message.getGameState() == getattr(constants, state+'GameState'):
                self.newEvents.add(getattr(events, 'EVENT_SWITCHED_TO_'+state.upper()+'_GAME_STATE'))

        # The next time around, the present is the past and the future is the present.
        self._recordMessage(message)

    def calc_events(self, events, deferreds):
        # Add any event you have inferred from the last message you got from the game controller.
        for event in self.newEvents:
            events.add(event)
        # Don't refire these events unless they recur.
        self.newEvents.clear()



if __name__ == '__main__':
    welcome = "Testing the gamestatus module."
    print len(welcome)*"*" + "\n" + welcome + "\n" + len(welcome)*"*"
    print "No tests have been implemented, thus far."
