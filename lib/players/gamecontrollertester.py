#!/usr/bin/python


import player_init
from burst_util import DeferredList
from burst.player import Player
from burst.events import *
from burst.consts import *
import burst.moves as moves
from math import cos, sin
import time
from burst.walkparameters import WalkParameters
from burst.moves.walks import Walk
import os
from burst import events
import sys

class GameControllerTester(Player):
    
    def onStart(self):
        for attribute in dir(events):
            if attribute[:5] == "EVENT" and not attribute in ['EVENT_TIME_EVENT', 'EVENT_STEP', 'EVENT_BALL_IN_FRAME', 'EVENT_BALL_BODY_INTERSECT_UPDATE']:
                print "Registering event", attribute
                self._eventmanager.register(getattr(events, attribute[:]),
                    lambda attribute=attribute: sys.stdout.write(attribute[:]+"\n"))



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(GameControllerTester)
#    mainloop.setCtrlCCallback(moduleCleanup)
    mainloop.run()
    #burst.getMotionProxy().getRemainingFootStepCount()

