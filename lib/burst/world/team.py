from ..events import EVENT_ALL_YELLOW_GOAL_SEEN

BLUE_GOAL, YELLOW_GOAL = 1, 2

class Team(object):
    def __init__(self, world):
        # TODO: team info such as which team we are on, etc., is gotten from the game
        # controller, which we are currently missing.
        self._world = world
        self.setupBlueTeam()

    def setupBlueTeam(self):
        self.target_goal = YELLOW_GOAL
        self.our_goal = (self.target_goal is BLUE_GOAL and YELLOW_GOAL) or BLUE_GOAL
        # this is the event we check in order to calculate stuff
        self.target_goal_seen_event = EVENT_ALL_YELLOW_GOAL_SEEN
        self.left_post, self.right_post = self._world.yglp, self._world.ygrp


