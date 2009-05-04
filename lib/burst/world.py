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
        if (abs(self.bearing - new_bearing) > MIN_BEARING_CHANGE or
                abs(self.dist - new_dist) > MIN_DIST_CHANGE):
            events.add(EVENT_BALL_POSITION_CHANGED)
        # store new values
        (self.bearing, self.centerX, self.centerY, self.confidence,
                self.dist, self.elevation, self.focDist, self.height,
                    self.width) = ball_state
        self.seen = new_seen
        return events

class World(object):

    def __init__(self):
        self._memory = burst.getMemoryProxy()
        self._events = set()

        # Stuff that we prefer the users use directly doesn't get a leading underscore
        self.ball = Ball(self._memory)

    def update(self):
        self._events.update(self.ball.update())

    def getEvents(self):
        events = self._events
        self._events = set()
        return events

