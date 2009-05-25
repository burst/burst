#import burst
#from burst.consts import *
#from events import *


__all__ = ['Message', 'BOTH_TEAMS', 'ALL_ROBOTS_OF_AFFECTED_TEAM', 'TransitionToInitialState', 'TransitionToReadyState',
            'TransitionToSetState', 'TransitionToPlayingState', 'TransitionToPenalizedState', 'TransitionToFinishedState']


ALL_ROBOTS_OF_AFFECTED_TEAM = 0
BOTH_TEAMS = 0


class ParseError(Exception):
    pass



class Registrat(type):
	registered = []
	def __new__(cls, name, bases, dct):
		clazz = type.__new__(cls, name, bases, dct)
		Registrat.registered.append(clazz)
		return clazz



# TODO: This isn't proper documentation.
# Messages are of the following form: <affected team> <affected robot> <state to transition to> (additional modifiers optional)
class Message(object):
    
    __metaclass__ = Registrat

    keyword = ""

    def __init__(self, affectedTeam, affectedRobot):
        self.affectedTeam = affectedTeam
        self.affectedRobot = affectedRobot

    def serialize(self):
        return str(self.affectedTeam) + " " + str(self.affectedRobot) + " " + str(self.keyword)

    @staticmethod
    def deserialize(messageString):
        (affectedTeam, affectedRobot, msg) = tuple(messageString.split(' ')[0:3])
        for transitionState in Registrat.registered:
            if msg == transitionState.keyword:
                return transitionState(affectedTeam, affectedRobot)
        raise Exception("A malformed message was received.")

    @staticmethod
    def parse(string):
        if len(string.split(' ')) != 3:
            raise ParseError
        teamColor, robotNumber, cmd = tuple(string.split(' '))
        for cls in Registrat.registered:
            if cls.keyword == cmd:
                return cls(int(teamColor), int(robotNumber))
        raise ParseError




class TransitionToInitialState(Message):
    keyword = "initial"


class TransitionToReadyState(Message):
    keyword = "ready"


class TransitionToSetState(Message):
    keyword = "set"


class TransitionToPlayingState(Message):
    keyword = "playing"


class TransitionToPenalizedState(Message):
    keyword = "penalized"


class TransitionToFinishedState(Message):
    keyword = "finished"

