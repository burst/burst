#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_consts import DEG_TO_RAD
from burst.behavior import InitialBehavior
from burst_consts import *
import burst.actions as actions
import burst.moves as moves
from burst.world import World

"""
Circle Strafing tester. Test the choreograph moves for circle tracing,
later the actions calls for same.
"""

class turnccw(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.counter = 0
        #self._eventanager.register(self.onKickingPointChanged, EVENT_KP_CHANGED)
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

        if self.counter < 25:
            self._actions.executeTurnCCW().onDone(self.onTurnDone)
            return

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(turnccw).run()

