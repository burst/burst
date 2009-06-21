#!/usr/bin/python


import player_init
from burst.player import Player
import burst_events

THRESHOLD = 0.15

class Kicker(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self.obj = self._world.ball
        self.tracker = self._actions.tracker
        self.searcher = self._actions.searcher
        self.searcher.search([self.obj], True).onDone(self.onObjectFound)
        self._eventmanager.register(self.printtt, burst_events.EVENT_STEP)

    def printtt(self):
        return
        print self.obj.bearing

    def onObjectFound(self):
        print 'a'
        self.tracker.track(self.obj)
        print 'move'
        self.strafe()

    def strafe(self):
        move = False
        if self.obj.bearing < -THRESHOLD:
            self._actions.executeTurnCW().onDone(self.strafe)
        elif self.obj.bearing > THRESHOLD:
            self._actions.executeTurnCCW().onDone(self.strafe)
        else:
            self.onArrivedAtPosition()
        
    
    def onArrivedAtPosition(self):
        print 'Goal reached!'
        self._actions.sitPoseAndRelax()
        self._eventmanager.quit()




if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
