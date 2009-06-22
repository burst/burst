#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_events import *
from burst.behavior import InitialBehavior

dt1 = 10.0
dt2 = 20.0

class FrameRateTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        # Down, Left, Up, Right - learn your directions!
        print "wait %s" % dt1
        self._eventmanager.callLater(dt1, self.lowFramerate)

    def lowFramerate(self):
        print "setting 10 fps"
        self._actions.setCameraFrameRate(10).onDone(self.lowFramerateDone)

    def lowFramerateDone(self):
        print "wait %s" % dt2
        self._eventmanager.callLater(dt2, self.highFramerate)

    def highFramerate(self):
        print "setting 20 fps"
        self._actions.setCameraFrameRate(20).onDone(self.onQuit)

    def onQuit(self):
        print "quitting"
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(FrameRateTester).run()

