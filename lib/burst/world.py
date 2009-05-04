import burst
from events import *

MIN_BEARING_CHANGE = 1e-3 # TODO - ?
MIN_DIST_CHANGE = 1e-3

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

    def update(self):
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

    def update(self):
        """ get new values from proxy, return set of events """
        events = set()
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?
        (new_angleX, new_angleY, new_bearing, new_centerX, new_centerY,
                new_dist, new_elevation, new_focDist, new_height,
                new_leftOpening, new_rightOpening, new_x, new_y, new_shotAvailable,
                    new_width) = new_state = self._memory.getListData(self._vars)
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
                    self.width) = new_state
        self.seen = new_seen
        return events

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
        self._objects = [self.ball, self.bglp, self.bgrp, self.yglp, self.ygrp]

    def update(self):
        if self._motion.getRemainingFootStepCount() == 0:
            self._events.add(EVENT_WALK_DONE)
        for obj in self._objects:
            self._events.update(obj.update())
        if self.bglp.seen and self.bgrp.seen:
            self._events.add(EVENT_ALL_BLUE_GOAL_SEEN)
        if self.yglp.seen and self.ygrp.seen:
            self._events.add(EVENT_ALL_YELLOW_GOAL_SEEN)

    def getEvents(self):
        events = self._events
        self._events = set()
        return events

