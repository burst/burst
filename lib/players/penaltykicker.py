#!/usr/bin/python


import player_init
from burst.player import Player
from burst import events
import sys


class PenaltyKicker(Player):
    
    def onStart(self):
        for attribute in dir(events):
            if attribute[:5] == "EVENT" and not attribute in ['EVENT_TIME_EVENT', 'EVENT_STEP', 'EVENT_BALL_IN_FRAME', 
                'EVENT_BALL_BODY_INTERSECT_UPDATE', 'EVENT_BALL_POSITION_CHANGED']:
                self._eventmanager.register(getattr(events, attribute[:]),
                    lambda attribute=attribute: sys.stdout.write(attribute[:]+"\n"))
        self._eventmanager.register(events.EVENT_SWITCHED_TO_PLAY_GAME_STATE, self.onGameStart)

    def onGameStart(self):
        self._actions.kickBall().onDone(self.onKickComplete)
    
    def onKickComplete(self):
        self._eventmanager.quit()


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(PenaltyKicker).run()
