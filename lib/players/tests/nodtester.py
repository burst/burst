#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.behavior import InitialBehavior

class Nod(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.callLater(2.5, self.registerSomethingOnHeadMove)
        self.doNod()

    def doNod(self):
        self.log("Will Nod")
        # Down, Left, Up, Right - learn your directions!
        nods = [(0.0, 0.0), (0.0, 0.5), (0.0, 0.0), (0.5, 0.0),
            (0.0, 0.0), (0.0, -0.5), (0.0, 0.0), (-0.5, 0.0),
            (0.0, 0.0)]
        self._actions.chainHeads(nods).onDone(self._eventmanager.quit)

    def registerSomethingOnHeadMove(self):
        self.log("using getCurrentHeadBD")
        self._actions.getCurrentHeadBD().onDone(self.saySomething)

    def saySomething(self):
        self.log("done with current head action")

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Nod).run()

