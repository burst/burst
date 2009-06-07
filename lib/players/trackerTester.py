#!/usr/bin/python

import player_init

from burst.player import Player
import burst.moves as moves

class trackerTester(Player):
    
    def onStart(self):
        self.count = 1
        self._actions.initPoseAndStiffness().onDone(self.initHeadPosition)
    
    def initHeadPosition(self):
        self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_FAR).onDone(self.track)
    
    def track(self):
        print "trackerTester: TRACKING %s" % (self.count)
        self.count += 1
        self._actions.tracker.track(self._world.ball, on_lost_callback=self.trackNextFrame)

    def trackNextFrame(self):
        self._eventmanager.callLater(0.0, self.track)

    def wrapUp(self):
        print "tracker lost the ball"
        self._eventmanager.quit()
        

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(trackerTester).run()

