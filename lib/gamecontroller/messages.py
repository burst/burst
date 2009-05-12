#import burst
#from burst.consts import *
#from events import *


__all__ = ['Message', 'BOTH_TEAMS', 'ALL_ROBOTS_OF_AFFECTED_TEAM']


ALL_ROBOTS_OF_AFFECTED_TEAM = 999
BOTH_TEAMS = 999


class Message(object):
    
    def __init__(self, affectedTeam, affectedRobot):
        pass

    def serialize(self):
        pass

    @staticmethod
    def deserialize(messageString):
        pass


class TransitionToInitialState(Message):
    pass


class TransitionToReadyState(Message):
    pass


class TransitionToSetState(Message):
    pass


class TransitionToPlayingState(Message):
    pass


class TransitionToPenalizedState(Message):
    pass


class TransitionToFinishedState(Message):
    pass
