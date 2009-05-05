from math import cos, sin, sqrt, pi

import burst
from events import *

MIN_BEARING_CHANGE = 1e-3 # TODO - ?
MIN_DIST_CHANGE = 1e-3

DEG_TO_RAD = pi / 180.0

class Ball(object):

    def __init__(self, memory):
        self._memory = memory
        self._ball_vars = ['/BURST/Vision/Ball/%s' % s for s in "bearing centerX centerY confidence dist elevation focDist height width".split()]

        self.bearing = 0.0
        self.centerX = 0.0
        self.centerY = 0.0
        self.confidence = 0.0
        self.dist = 0.0
        self.elevation = 0.0
        self.focDist = 0.0
        self.height = 0.0
        self.width = 0.0
        self.seen = False

    def calc_events(self):
        """ get new values from proxy, return set of events """
        events = set()
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?
        (new_bearing, new_centerX, new_centerY, new_confidence,
                new_dist, new_elevation, new_focDist, new_height,
                    new_width) = ball_state = self._memory.getListData(self._ball_vars)
        # calculate events
        new_seen = (new_dist > 0.0)
        if new_seen:
            events.add(EVENT_BALL_IN_FRAME)
        if self.seen and not new_seen:
            events.add(EVENT_BALL_LOST)
        if not self.seen and new_seen:
            events.add(EVENT_BALL_SEEN)
        # TODO: we should only look at the localization supplied ball position,
        # and not the position in frame (image coordinates) or the relative position,
        # which may change while the ball is static.
        if new_seen and (abs(self.bearing - new_bearing) > MIN_BEARING_CHANGE or
                abs(self.dist - new_dist) > MIN_DIST_CHANGE):
            events.add(EVENT_BALL_POSITION_CHANGED)
        # store new values
        (self.bearing, self.centerX, self.centerY, self.confidence,
                self.dist, self.elevation, self.focDist, self.height,
                    self.width) = ball_state
        self.seen = new_seen
        return events

class Robot(object):
    def __init__(self, memory, motion):
        self._memory = memory
        self._motion = motion
        self.isWalkingActive = False
        self.isTurningActive = False
        self.walkID = 0
        self.turnID = 0
        
    def calc_events(self):
        """ get new values from proxy, return set of events """
        events = set()
        if self.isWalkingActive and not self._motion.isRunning(self.walkID): #self._motion.getRemainingFootStepCount() == 0 doesn't work in webots
            self.isWalkingActive = False
            events.add(EVENT_WALK_DONE)
        if self.isTurningActive and not self._motion.isRunning(self.turnID):
            self.isTurningActive = False
            events.add(EVENT_TURN_DONE)
        return events
        

class GoalPost(object):

    def __init__(self, memory, name, position_changed_event):
        self._memory = memory
        self._name = name
        self._position_changed_event = position_changed_event
        template = '/BURST/Vision/%s/%%s' % name
        self._vars = [template % s for s in ['AngleXDeg', 'AngleYDeg',
            'BearingDeg', 'CenterX', 'CenterY', 'Distance', 'ElevationDeg',
         'FocDist', 'Height', 'LeftOpening', 'RightOpening', 'Width', 'X', 'Y',
         'shotAvailable']]

        self.angleX = 0.0
        self.angleY = 0.0
        self.bearing = 0.0
        self.centerX = 0.0
        self.centerY = 0.0
        self.dist = 0.0
        self.elevation = 0.0
        self.focDist = 0.0
        self.height = 0.0
        self.leftOpening = 0.0
        self.rightOpening = 0.0
        self.width = 0.0
        self.x = 0.0
        self.y = 0.0
        self.shotAvailable = 0.0
        self.seen = False

    def calc_events(self):
        """ get new values from proxy, return set of events """
        events = set()
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?
        (new_angleX, new_angleY, new_bearing, new_centerX, new_centerY,
                new_dist, new_elevation, new_focDist, new_height,
                new_leftOpening, new_rightOpening, new_x, new_y, new_shotAvailable,
                    new_width) = new_state = self._memory.getListData(self._vars)
        # convert to radians
        new_bearing *= DEG_TO_RAD
        # calculate events
        new_seen = (new_dist > 0.0)
        # TODO: we should only look at the localization supplied ball position,
        # and not the position in frame (image coordinates) or the relative position,
        # which may change while the ball is static.
        if new_seen and (abs(self.bearing - new_bearing) > MIN_BEARING_CHANGE or
                abs(self.dist - new_dist) > MIN_DIST_CHANGE):
            events.add(self._position_changed_event)
        # store new values
        (self.angleX, self.angleY, self.bearing, self.centerX, self.centerY,
                self.dist, self.elevation, self.focDist, self.height,
                self.leftOpening, self.rightOpening, self.x, self.y, self.shotAvailable,
                  self.width) = (new_angleX, new_angleY, new_bearing, new_centerX,
                  new_centerY, new_dist, new_elevation, new_focDist, new_height,
                  new_leftOpening, new_rightOpening, new_x, new_y, new_shotAvailable,
                  new_width)
        self.seen = new_seen
        return events

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

class Computed(object):
    """ place holder for any computed value, currently just the kicking point, that
    doesn't naturally belong to any other object, like ball speed etc
    """
    def __init__(self, world):
        self._world = world
        self._team = world.team
        # Kick Point
        self.kp = None
        self.kp_valid = False
        self.kp_k = 30.0

    def calc_events(self):
        events = set()
        if self._team.target_goal_seen_event in self._world._events:
            new_kp = self.calculate_kp()
            if not self.kp_valid or (new_kp[0] - self.kp[0] > 1e-5 or new_kp[1] - self.kp[1] > 1e-5):
                events.add(EVENT_KP_CHANGED)
            self.kp_valid = True
            self.kp = new_kp
        else:
            # cache the kp value it self until a new one comes
            self.kp_valid = False
        return events

    def calculate_kp(self):
        """ Our kicking point, first iteration, is a point k distant from the ball
        along the line connecting the point in the middle of the target goal
        and the ball in the outward direction.

        The coordinate system is not standard: the x axis is to the right of the robot,
        the y axis is to the front. The bearing is measured from the y axis ccw.
        """
        # left - l, right - r, bearing - b, dist - d
        team = self._team
        left_post, right_post, ball = team.left_post, team.right_post, self._world.ball
        lb, ld, rb, rd = (left_post.bearing, left_post.dist,
                right_post.bearing, right_post.dist)
        bb, bd = ball.bearing, ball.dist
        bx, by = bd * sin(bb), bd * cos(bd)
        k = self.kp_k
        cx = (rd * sin(rb) + ld * sin(lb)) / 2.0
        cy = (rd * cos(rb) + ld * cos(lb)) / 2.0
        nx, ny = bx - cx, by - cy
        nnorm = sqrt(nx**2 + ny**2)
        nx, ny = nx / nnorm, ny / nnorm
        kpx, kpy = bx + k * nx, by + k * ny
        print "KP: b (%3.3f, %3.3f), c(%3.3f, %3.3f), n(%3.3f, %3.3f), kp(%3.3f, %3.3f)" % (bx, by, cx, cy, nx, ny, kpx, kpy)
        return kpx, kpy

class World(object):

    def __init__(self):
        self._memory = burst.getMemoryProxy()
        self._motion = burst.getMotionProxy()
        self._events = set()

        # Stuff that we prefer the users use directly doesn't get a leading underscore
        self.ball = Ball(self._memory)
        self.bglp = GoalPost(self._memory, 'BGLP', EVENT_BGLP_POSITION_CHANGED)
        self.bgrp = GoalPost(self._memory, 'BGRP', EVENT_BGRP_POSITION_CHANGED)
        self.yglp = GoalPost(self._memory, 'YGLP', EVENT_YGLP_POSITION_CHANGED)
        self.ygrp = GoalPost(self._memory, 'YGRP', EVENT_YGRP_POSITION_CHANGED)
        self.robot = Robot(self._memory, self._motion)
        # construct team after all the posts are constructed, it keeps a reference to them.
        self.team = Team(self)
        self.computed = Computed(self)

        # all objects that we delegate the event computation and naoqi interaction to.
        # TODO: we have the exact state of B-HUMAN, so we could use exactly their solution,
        # and hence this todo. We have multiple objects that calculate their events
        # based on ground truths (naoqi proxies) and on calculated truths. We need to
        # rerun them every time something is updated, *in the correct order*. So right
        # now I'm hardcoding this by using an ordered list of lists, but later this
        # should be calculated by storing a "needed" and "provided" list, just like B-HUMAN,
        # and doing the sorting once (and that value can be cached to avoid recomputing on
        # each run).
        self._objects = [
            # All basic objects that rely on just naoproxies should be in the first list
            [self.ball, self.bglp, self.bgrp, self.yglp, self.ygrp, self.robot],
            # anything that relies on basics but nothing else should go next
            [self],
            # self.computed should always be last
            [self.computed],
        ]

    def calc_events(self):
        """ World treats itself as a regular object by having an update function,
        this is called after the basic objects and before the computed object (it
        may set some events / variables needed by the computed object)
        """
        events = set()
        if self.bglp.seen and self.bgrp.seen:
            events.add(EVENT_ALL_BLUE_GOAL_SEEN)
        if self.yglp.seen and self.ygrp.seen:
            events.add(EVENT_ALL_YELLOW_GOAL_SEEN)
        return events

    def update(self):
        # TODO: automatic calculation of event dependencies (see constructor)
        for objlist in self._objects:
            for obj in objlist:
                self._events.update(obj.calc_events())


    def getEvents(self):
        events = self._events
        self._events = set()
        return events

