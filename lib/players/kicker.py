#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.behavior import InitialBehavior
import burst

class Kicker(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.kick().onDone(self.onKickComplete)

    def kick(self):
        target_left_right_posts = [self._world.yglp, self._world.ygrp]
#        target_left_right_posts = [self._world.bglp, self._world.bgrp]
        return self._actions.kickBall(target_left_right_posts=target_left_right_posts)

    def onKickComplete(self):
        print "kick complete"
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
