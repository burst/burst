#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.events import *
from burst_consts import *
from burst.player import Player
from burst.events import *
from burst_consts import *
import burst.actions as actions
import burst.moves as moves
from burst.world import World
from math import cos, sin


def pr(s):
    print s

class Passing(Player):

    def onStart(self):
        # go to init position
        self._actions.initPoseAndStiffness()

        # Kick with left
        print "Left kick!"
        self._actions.kick(actions.KICK_TYPE_STRAIGHT_WITH_LEFT).onDone(doQuit)

    def doQuit(self):
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Passing).run()

