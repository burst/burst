#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst.events import EVENT_BALL_IN_FRAME, EVENT_BALL_SEEN, EVENT_BALL_LOST, EVENT_CHANGE_LOCATION_DONE, EVENT_ALL_YELLOW_GOAL_SEEN
from burst.consts import DEG_TO_RAD, IMAGE_HALF_WIDTH, IMAGE_HALF_HEIGHT, LEFT, RIGHT
from burst.player import Player
import burst.actions as actions
import burst.moves as moves
from burst.world import World
from math import cos, sin
from burst_util import calculate_middle, calculate_relative_pos, polar2cart, cart2polar

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
