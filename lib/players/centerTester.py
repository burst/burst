#!/usr/bin/python

import player_init

from burst.player import Player

class centerTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness().onDone(
            lambda: self._actions.tracker.center(self._world.ball)).onDone(
            self.wrapUp)
    
    def wrapUp(self):
        print "center done"
        print "calling center again to make sure it works when already centered"
        self._actions.tracker.center(self._world.ball).onDone(self.reallyWrapUp)

    def reallyWrapUp(self):
        print "centered again!"
        self._eventmanager.quit()
 

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(centerTester).run()

