#!/usr/bin/python


import player_init
from burst.player import Player
import burst.events as events
import sys


class SonarTester(Player):
    
    def onStart(self):
        super(SonarTester, self).onStart()
        for attribute in dir(events):
            if attribute[:5] == "EVENT" and attribute in ['EVENT_SONAR_OBSTACLE_IN_FRAME', 'EVENT_SONAR_OBSTACLE_SEEN', 'EVENT_SONAR_OBSTACLE_LOST']:
                self._eventmanager.register(lambda attribute=attribute: sys.stdout.write(attribute[:]+"\n"), getattr(events, attribute[:]))



if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(SonarTester)
    mainloop.run()
