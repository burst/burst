#!/usr/bin/python


import player_init
from burst_util import DeferredList
from burst.player import Player
from burst.events import *
from burst_consts import *
import burst.moves as moves
from burst.walkparameters import WalkParameters
from burst.moves.walks import Walk
from burst import events
import sys

class EventsTester(Player):
    
    def onStart(self):
        super(EventsTester, self).onStart()
        for attribute in dir(events):
            if attribute[:5] == "EVENT" and not attribute in ['EVENT_TIME_EVENT', 'EVENT_STEP', 'EVENT_BALL_IN_FRAME',
                'EVENT_BALL_BODY_INTERSECT_UPDATE', 'EVENT_LEFT_BUMPER_PRESSED', 'EVENT_RIGHT_BUMPER_PRESSED', 'EVENT_CHEST_BUTTON_PRESSED']:
                self._eventmanager.register(lambda attribute=attribute: sys.stdout.write(attribute[:]+"\n"), getattr(events, attribute[:]))



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(EventsTester)
    mainloop.run()
