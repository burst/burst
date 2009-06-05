#!/usr/bin/python


import player_init
from burst.player import Player
from burst.events import *


class SonarTester(Player):

    def __init__(self, *args, **kw):
        super(SonarTester, self).__init__(*args, **kw)

    def printtt(self, x):
        print x

    def onStart(self):
        self._eventmanager.register(self.getSonars, EVENT_STEP)

    def getSonars(self):
        a = self._world.robot.sonars.leftSonar.readDistance()
        b = self._world.robot.sonars.rightSonar.readDistance()
        print "%3.3f %3.3f" % (a,b)

    def onStop(self):
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(SonarTester).run()
