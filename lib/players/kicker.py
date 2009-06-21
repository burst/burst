#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.behavior import InitialBehavior
import burst

class Kicker(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._ballkicker = self.kick()
        self._ballkicker.onDone(self.onKickComplete)

    def stop_complete(self):
        # return a bd to complete on stop
        return self._ballkicker.stop()

    def kick(self):
        target_left_right_posts = [self._world.yglp, self._world.ygrp]
#        target_left_right_posts = [self._world.bglp, self._world.bgrp]
        return self._actions.kickBall(target_left_right_posts=target_left_right_posts)

    def onKickComplete(self):
        print "kick complete - TODO: don't quit"
        self._eventmanager.quit()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()

