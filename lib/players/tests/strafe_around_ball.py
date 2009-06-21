#!/usr/bin/python


import player_init
from burst.behavior import InitialBehavior
import burst_events

THRESHOLD = 0.15

class StrafeAroundBall(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
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
    from burst.eventmanager import MainLoop
    MainLoop(StrafeAroundBall).run()

