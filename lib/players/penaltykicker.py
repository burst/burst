#!/usr/bin/python


import player_init
from burst.behavior import InitialBehavior
import burst_events
import sys


class PenaltyKicker(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        for attribute in dir(burst_events):
            if attribute[:5] == "EVENT" and not attribute in ['EVENT_TIME_EVENT', 'EVENT_STEP', 'EVENT_BALL_IN_FRAME', 
                'EVENT_BALL_BODY_INTERSECT_UPDATE', 'EVENT_BALL_POSITION_CHANGED']:
                self._eventmanager.register(getattr(burst_events, attribute[:]),
                    lambda attribute=attribute: sys.stdout.write(attribute[:]+"\n"))
        self._eventmanager.register(burst_events.EVENT_SWITCHED_TO_PLAY_GAME_STATE, self.onGameStart)

    def onGameStart(self):
        self._actions.kickBall().onDone(self.onKickComplete)
    
    def onKickComplete(self):
        self._eventmanager.quit()


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(PenaltyKicker).run()
