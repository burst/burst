#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.player import Player
import burst

class Kicker(Player):
    
    def onStart(self):
        if burst.options.game_controller:
            print "Waiting for game controller Playing state"
            super(Kicker, self).onStart()
        else:
            self._realStart()
    
    def enterGame(self):
        self._realStart()

    def _realStart(self):
        self._actions.initPoseAndStiffness().onDone(self._actions.kickBall).onDone(self.onKickComplete)

    def onKickComplete(self):
        print "kick complete"
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()
