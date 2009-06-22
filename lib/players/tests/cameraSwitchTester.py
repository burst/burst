#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_consts import CAMERA_WHICH_TOP_CAMERA, CAMERA_WHICH_BOTTOM_CAMERA
from burst.behavior import InitialBehavior

class CameraSwitchTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        # Down, Left, Up, Right - learn your directions!
        self._actions.setCamera(CAMERA_WHICH_TOP_CAMERA).onDone(
            lambda: self._eventmanager.callLater(2.0, self.setBottomCamera))

    def setBottomCamera(self):
        self._actions.setCamera(CAMERA_WHICH_BOTTOM_CAMERA).onDone(
            self._eventmanager.quit)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(CameraSwitchTester).run()

