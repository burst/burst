#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.behavior import InitialBehavior
import burst.moves.poses as poses
import burst

class Kicker(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.STRAIGHT_WALK_INITIAL_POSE)

    def _start(self, firstTime=False):
        self._ballkicker = self.kick()
        self._ballkicker.onDone(self.onKickComplete)

    def _stop(self):
        return self._ballkicker.stop()

    def kick(self):
        target_left_right_posts = [self._world.opposing_lp, self._world.opposing_rp]
        return self._actions.kickBall(target_left_right_posts=target_left_right_posts)

    def onKickComplete(self):
        print "kick complete - currently Player will restart me, just let it."
        self.stop()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()

