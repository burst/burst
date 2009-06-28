#!/usr/bin/python

import player_init

from burst.behavior import InitialBehavior

class centerTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        # use the currently seen object, randomly (or not) the first
        self.log("Switching to Top to look for a single goal post")
        DT = 0.0 # now that there is a CAMERA_SWITCH_WAIT It should also allow for the
                 # few frames I wanted to register existing objects.
        self._actions.switchToTopCamera().onDone(lambda:
            self._eventmanager.callLater(DT, self.findCenteringTarget))

    def findCenteringTarget(self):
        possible_targets = list(set(self._world.seenObjects())&set(self._world.all_posts))
        if len(possible_targets) == 0:
            self.log("No targets to center on, no visible posts")
            return self.stop()
        self.log("Centering on %s" % possible_targets[0])
        self._actions.centerer.start(target=possible_targets[0], lostCallback=self.onLost
            ).onDone(self.wrapUp)

    def onLost(self):
        self.log("lost ball")
        self.stop()

    def wrapUp(self):
        self.log("calling center again to make sure it works when already centered")
        self._actions.centerer.start(target=self._world.ball).onDone(self.reallyWrapUp)

    def reallyWrapUp(self):
        self.log("centered again!")
        self.stop()


if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(centerTester).run()

