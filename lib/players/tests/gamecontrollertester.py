#!/usr/bin/python

import os
import sys
import time
from math import cos, sin

import player_init

from burst_util import DeferredList
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst_events
import burst.moves as moves
from burst.walkparameters import WalkParameters
from burst.moves.walks import Walk

class GameControllerTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        for attribute in dir(burst_events):
            if attribute.startswith("EVENT") and attribute not in ['EVENT_TIME_EVENT', 'EVENT_STEP', 'EVENT_BALL_IN_FRAME',
                'EVENT_BALL_BODY_INTERSECT_UPDATE', 'EVENT_LEFT_BUMPER_PRESSED', 'EVENT_RIGHT_BUMPER_PRESSED', 'EVENT_CHEST_BUTTON_PRESSED']:
                self._eventmanager.register(
                    lambda attribute=attribute: sys.stdout.write(attribute+"\n"),
                    getattr(burst_events, attribute))


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(GameControllerTester)
    mainloop.run()
