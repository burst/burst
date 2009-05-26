#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.player import Player

class Kicker(Player):
    
    def onStart(self):
        self._actions.kickBall().onDone(self.onKickComplete)
    
    def onKickComplete(self):
        print "kick complete"
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
