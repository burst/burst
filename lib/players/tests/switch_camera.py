#!/usr/bin/python

import player_init

from burst.behavior import Behavior

class SwitchCamera(Behavior):

    def _start(self, firstTime=False):
        self._actions.initPoseAndStiffness().onDone(self.startTen)

    def startTen(self):
        cl = self._eventmanager.callLater
        for i in xrange(10):
            cl(float(i)*2 + 1.0, self._actions.switchToTopCamera)
            cl(float(i)*2 + 2.0, self._actions.switchToBottomCamera)
        cl(25.0, self._eventmanager.quit)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(SwitchCamera).run()

