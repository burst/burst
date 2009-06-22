#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.behavior import InitialBehavior

class HeadAndWalkTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=None)

    def _start(self, firstTime=False):
        self._actions.moveHead(-0.5,0.0).onDone(self.doTest)

    def doTest(self):
        # Down, Left, Up, Right - learn your directions!
        self._eventmanager.callLater(3.5, self.moveHead)
        self._actions.changeLocationRelative(50.0, 0.0, 0.0)

    def moveHead(self):
        self._actions.moveHead(0.5,0.0).onDone(self._eventmanager.quit)

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(HeadAndWalkTester).run()

