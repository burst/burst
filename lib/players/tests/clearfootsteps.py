#!/usr/bin/python

import player_init

from burst.player import Player

class Clearfootsteps(Player):

    # TODO

    def onStart(self):
        self._actions.initPoseAndStiffness().onDone(self.start)

    def start(self):
        self._actions.changeLocationRelative(500.0, 0.0, 0.0)
        self._eventmanager.callLater(2.0, self._actions.clearFootsteps)

    def cancelWalk(self):
        self._actions.cancelWalk()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Clearfootsteps).run()
