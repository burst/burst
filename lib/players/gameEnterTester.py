#!/usr/bin/python

import player_init
from burst.player import Player
from burst.events import *
from burst_consts import *
import burst.moves as moves

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0
TIME_WAITING = 3 #time to wait when finishing the leap for getting up
WAITING_FOR_HEAD = 5

class GameEnter(Player):

    def onStart(self):
        super(GameEnter, self).onStart()
        self.isPenalty = False # TODO: Use the gameStatus object.
        self.isWebots = True

    def enterGame(self):
        self._actions.say("game enter tester in play")

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(GameEnter).run()


