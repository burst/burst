from ..events import EVENT_ALL_YELLOW_GOAL_SEEN

BLUE_GOAL, YELLOW_GOAL = 1, 2

class Posts(object):
    """ Helper object to hold the posts of a goal, and access
    left/right top/bottom or as a pair (left_right)
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right
        if self.left.world_y > self.right.world_y:
            self.top, self.bottom = self.left, self.right
        else:
            self.top, self.bottom = self.right, self.left
        self.left_right = (self.left, self.right)

class Team(object):
    def __init__(self, world):
        # TODO: team info such as which team we are on, etc., is gotten from the game
        # controller, which we are currently missing.
        self._world = world
        self.info = {
            YELLOW_GOAL: {'posts': (self._world.yglp, self._world.ygrp),
                'other_goal': BLUE_GOAL},
            BLUE_GOAL: {'posts': (self._world.bglp, self._world.bgrp),
                'other_goal': YELLOW_GOAL},
               }

        # TODO - get this info from gamecontroller
        self.setupBlueTeam()

    def setupBlueTeam(self):
        self.target_goal = YELLOW_GOAL

        self.our_goal = self.info[self.target_goal]['other_goal']
        self.target_posts = Posts(*self.info[self.target_goal]['posts'])
        # this is the event we check in order to calculate stuff
        self.target_goal_seen_event = EVENT_ALL_YELLOW_GOAL_SEEN
        self.left_post, self.right_post = self._world.yglp, self._world.ygrp


