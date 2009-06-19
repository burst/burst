#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.player import Player
import burst

class Kicker(Player):
    
    def onStart(self):
        if burst.options.game_controller:
            print "Waiting for game controller Playing state"
            self._actions.say('initial')
            super(Kicker, self).onStart()
        else:
            self._realStart()
    
    def enterGame(self):
        self._realStart()

    def _realStart(self):
        self.kick().onDone(self.onKickComplete)

    def kick(self):
#        target_left_right_posts = [self._world.yglp, self._world.ygrp]
        target_left_right_posts = [self._world.bglp, self._world.bgrp]
        return self._actions.kickBall(target_left_right_posts=target_left_right_posts)

    def onKickComplete(self):
        print "kick complete"
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
