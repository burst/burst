#!/usr/bin/python


import player_init
from burst_util import DeferredList
from burst.player import Player
from burst_events import *
from burst_consts import *
import burst.moves as moves
from burst.walkparameters import WalkParameters
from burst.moves.walks import Walk
import sys

class EventsTester(Player):
    
    def onStart(self):
        super(EventsTester, self).onStart()
        for attribute in dir(burst_events):
#        for attribute in ['EVENT_YGRP_POSITION_CHANGED', 'EVENT_YGLP_POSITION_CHANGED']:
            if attribute[:5] == "EVENT" and not attribute in ['EVENT_TIME_EVENT', 'EVENT_STEP']:
                self._eventmanager.register(lambda attribute=attribute: sys.stdout.write(attribute[:]+"\n"), getattr(burst_events, attribute[:]))



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(EventsTester)
    mainloop.run()
