#!/usr/bin/python

import player_init

from burst.player import Player

class trackerTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness().onDone(
            lambda: self._actions.tracker.track(self._world.ball, on_lost_callback=self.wrapUp))
    
    def wrapUp(self):
        print "tracker lost the ball"
        self._eventmanager.quit()
        

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(trackerTester).run()

