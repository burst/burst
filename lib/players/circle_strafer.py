#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.events import EVENT_BALL_IN_FRAME, EVENT_BALL_SEEN, EVENT_BALL_LOST
from burst_consts import DEG_TO_RAD
from burst.player import Player
from burst.events import *
from burst_consts import *
import burst.actions as actions
import burst.moves as moves
from burst.world import World
from math import cos, sin

"""
Circle Strafing tester. Test the choreograph moves for circle tracing,
later the actions calls for same.
"""

class circle_strafer(Player):

    def onStart(self):
        self.counter = 0
        #self._eventanager.register(EVENT_KP_CHANGED, self.onKickingPointChanged)
        self._actions.initPoseAndStiffness()
        self._actions.executeCircleStraferInitPose().onDone(self.doNextAction)

        # do a quick search for kicking point
        #self._actions.executeCircleStrafer().onDone(self.onTurnDone)

    def onTurnDone(self):
        print "\nTurn done!: "
        print "******************"
        if (self.counter < 25):
            print "self.counter smaller then 25"
            self.counter = self.counter + 1
        self.doNextAction()
    
    def doNextAction(self):
        print "\ndoNextAction)"
        print "------------------"

        #if self.counter < 25 and (self.counter % 3) == 1:
        if self.counter < 25:      
            #self._actions.executeCircleStrafeClockwise().onDone(self.onTurnDone)
            self._actions.executeCircleStrafeCounterClockwise().onDone(self.onTurnDone)
            return
#        self.onTurnDone()        
#        return

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(circle_strafer).run()

