#!/usr/bin/python

__all__ = ['GameStatus', 'EmptyGameStatus']


import burst
from burst import events as events
import gamecontroller
from gamecontroller import constants as constants
from gamecontroller.constants import *
from burst.debug_flags import gamestatus_py_debug as debug
from burst.world.robot import LEDs
import burst_consts as consts


class PlayerStatus(object):
    '''
    Keeps track of the status of a single player.
    '''
    def __init__(self, teamColor, playerNumber):
        self.config(teamColor, playerNumber)
        self.playerStatus = UNKNOWN_PLAYER_STATUS

    def config(self, teamColor, playerNumber):
        self.teamColor = teamColor
        self.playerNumber = playerNumber

    def setStatus(self, status, remainingTimeForPenalty):
        self.status = status
        self.remainingTimeForPenalty = remainingTimeForPenalty

    def isPenalized(self):
        return self.status in constants.Penalties



class GameStatus(object):
    '''
    Each robot will host one instance of this class. It will be in charge of tracking the state of the game - who is penalized, what state
    the game is in (ready/set/play...), what the score is, etc. It will fire the appropriate events.
    '''

    def __init__(self, world, playerSettings):
        self.world = world # TODO: Right now, I only need this for the LEDs. Pass them instead?
        self.mySettings = playerSettings
        self.players = [[PlayerStatus(teamColor, playerNumber) for playerNumber in xrange(11)] for teamColor in xrange(2)] # TODO: Start at 0 or 1?
        self.newEvents = set()
        self.gameState = UNKNOWN_GAME_STATE # TODO
        self.reset()
        self.setColors()

    def reset(self):
        if debug:
            print "reseting"
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
        for team in xrange(2):
            for player in xrange(11):
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
            self.newEvents.add(events.EVENT_GOAL_SCORED_BY_MY_TEAM)
            self.newEvents.add(events.EVENT_GOAL_SCORED)
        if self.opposingTeamScore < message.getTeamScore(1 - self.mySettings.teamColor):
            self.newEvents.add(events.EVENT_GOAL_SCORED_BY_OPPOSING_TEAM)
            self.newEvents.add(events.EVENT_GOAL_SCORED)

    def _calcGameStateRelatedEvents(self, message):
        '''
        Calculates events that are related to the game state changing: the leaving of one game state, and the transition to a new one.
        '''
        for state in ['Initial', 'Ready', 'Set', 'Play', 'Finish']:
            if self.gameState == getattr(constants, state+'GameState') and message.getGameState() != getattr(constants, state+'GameState'):
                self.newEvents.add(getattr(events, 'EVENT_SWITCHED_FROM_'+state.upper()+'_GAME_STATE'))
            if self.gameState != getattr(constants, state+'GameState') and message.getGameState() == getattr(constants, state+'GameState'):
                self.newEvents.add(getattr(events, 'EVENT_SWITCHED_TO_'+state.upper()+'_GAME_STATE'))

    def _calcPenaltyRelatedEvents(self, message): # TODO: Rename.
        '''
        Calculates events that are related to a player's status (not necessarily one's own) being changed. Penalties, etc.
        '''
        for teamColor in xrange(2):
            for playerNumber in xrange(11):
                player = self.players[teamColor][playerNumber]
                # If something's changed:
                if player.status != message.getPenaltyStatus(teamColor, playerNumber):
                    # If switching to a penalty status:
                    if message.getPenaltyStatus(teamColor, playerNumber) in constants.Penalties and not player.status in constants.Penalties:
                        if player.teamColor == self.mySettings.teamColor:
                            if player.playerNumber == self.mySettings.playerNumber:
                                self.newEvents.add(events.EVENT_I_GOT_PENALIZED)
                            else:
                                self.newEvents.add(events.EVENT_TEAMMATE_PENALIZED)
                        else:
                            self.newEvents.add(events.EVENT_OPPONENT_PENALIZED)
                    # If returning from a penalty status:
                    if player.status in constants.Penalties and not message.getPenaltyStatus(teamColor, playerNumber) in constants.Penalties:
                        if player.teamColor == self.mySettings.teamColor:
                            if player.playerNumber == self.mySettings.playerNumber:
                                self.newEvents.add(events.EVENT_I_GOT_UNPENALIZED)
                            else:
                                self.newEvents.add(events.EVENT_TEAMMATE_UNPENALIZED)
                        else:
                            self.newEvents.add(events.EVENT_OPPONENT_UNPENALIZED)

    def _fireInitialEvents(self): # TODO: We'd might like to have the events fired in some predetermined order.
        for state in ['Initial', 'Ready', 'Set', 'Play', 'Finish']:
            if self.gameState == getattr(constants, state+'GameState'):
                self.newEvents.add(getattr(events, 'EVENT_SWITCHED_TO_'+state.upper()+'_GAME_STATE'))
        if self.players[self.mySettings.teamColor][self.mySettings.playerNumber].isPenalized():
            self.newEvents.add(events.EVENT_I_GOT_PENALIZED)

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
        for teamColor in xrange(2):
            for playerNumber in xrange(11):
                if self._isMe(teamColor, robotNumber):
                    return self.players[teamColor][playerNumber].status
        raise Exception("getMyPlayerStatus() - can't find myself among the players.")

    def changeKickOffTeam(kickOffTeam): # TODO: Untested.
        # TODO: I've been led to believe Python has properties/attributes/whatever, like C#. I probably just want to use that instead for the 
        # kickOffTeam variable, so that setColors() is called whenever it's changed.
        raise Exception("This feature has not yet been tested. It should work, but do test it before removing this line.")
        self.kickOffTeam = kickOffTeam
        self.setColors()

    def setColors(self):
        ''' Update the LEDs according to the information you carry. '''
        self.world.robot.leds.rightFootLED.turnOn(consts.TeamColors[self.kickOffTeam])



class EmptyGameStatus(object):
    '''
    An empty GameStatus object.
    '''
    def __init__(*args, **kw): pass
    def reset(*args, **kw): pass
    def readMessage(*args, **kw): pass
    def calc_events(*args, **kw): pass
    def getScore(*args, **kw): return 0
    def getMyPlayerStatus(*args, **kw): return Standard 



if __name__ == '__main__':
    welcome = "Testing the gamestatus module."
    print len(welcome)*"*" + "\n" + welcome + "\n" + len(welcome)*"*"
    print "No tests have been implemented, thus far."
