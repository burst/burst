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

#===============================================================================
#    Logic for Kicker:
# 
# 1. Scan for goal & ball
# 2. Calculate kicking-point (correct angle towards opponent goal), go as quickly as possible towards it (turn-walk-turn)
# 3. When near ball, go only straight and side-ways (align against leg closer to ball, and use relevant kick)
# 4. When close enough - kick!
# 
# Add states? add "closed-loop" (ball moved detection, robot moves incorrectly detection)
#
#
#
# 
# TODO:
# Add "k-p relevant" flag (to be made FALSE on start, when ball moves). Might not be necessary once localization kicks in
# Take bearing into account when kicking
# When finally approaching ball, use sidestepping instead of turning (only for a certain degree difference)
# When calculating k-p, take into account the kicking leg (use the one closer to opponent goal)
# 
# Add ball position cache (same as k-p local cache)
# Handle negative target location (walk backwards instead of really big turns...)
# What to do when near ball and k-p wasn't calculated?
# Handle case where ball isn't seen after front scan (add full scan inc. turning around) - hopefully will be overridden with ball from comm.
# Obstacle avoidance
#===============================================================================

#CAMERA_BEARING_OFFSET = 0.04 # cech = 0.04

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
