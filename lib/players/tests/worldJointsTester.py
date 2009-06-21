#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.events import *
from burst.behavior import InitialBehavior

class WorldJointsTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        # Down, Left, Up, Right - learn your directions!
        self._eventmanager.register(self.onStep, EVENT_STEP)

    def onStep(self):
        w = self._world
        print "%1.2f: %1.2f %1.2f" % (w.time, w.getAngle('HeadYaw'), w.getAngle('HeadPitch'))

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(WorldJointsTester).run()

