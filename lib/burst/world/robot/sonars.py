#!/usr/bin/python


from burst_consts import SONAR_OBSTACLE_THRESHOLD, SONAR_OBSTACLE_HYSTERESIS
from burst import events as events_module


# TODO: When several robots are next to each other, do their sonars collide?
class Sonars(object):

    _var = "extractors/alultrasound/distances"

    class Sonar(object):
        def __init__(self, side, world, index):
            self.side = side
            self.world = world
            self.index = index
        def readDistance(self):
            data = self.world.vars[Sonars._var]
            if len(data) == 0: # The sonar takes a while to warm up.
                return 1000.0 # This is a safe value that should cause no trouble to anyone.
            return data[self.index]

    class LeftSonar(Sonar):
        def __init__(self, world):
            super(Sonars.LeftSonar, self).__init__('Left', world, 0)

    class RightSonar(Sonar):
        def __init__(self, world):
            super(Sonars.RightSonar, self).__init__('Right', world, 1)

    def __init__(self, world):
        world._ultrasound.post.subscribe('', [500]) # TODO: See if we can lower this without any adverse effects.
        world.addMemoryVars([Sonars._var])
        self.leftSonar = Sonars.LeftSonar(world)
        self.rightSonar = Sonars.RightSonar(world)
        self.wasLastReadingBelowThreshold = False

    def setThreshold(self, threshold):
        SONAR_OBSTACLE_THRESHOLD = threshold

    def getThreshold(self):
        return SONAR_OBSTACLE_THRESHOLD

    def setHysteresis(self, hysteresis):
        SONAR_OBSTACLE_HYSTERESIS = hysteresis

    def getHysteresis(self):
        return SONAR_OBSTACLE_HYSTERESIS

    def readDistance(self):
        return min(self.rightSonar.readDistance(), self.leftSonar.readDistance())

    def calc_events(self, events, deferreds):
        distance = self.readDistance()
        if distance < SONAR_OBSTACLE_THRESHOLD:
            events.add(events_module.EVENT_SONAR_OBSTACLE_IN_FRAME)
            if not self.wasLastReadingBelowThreshold:
                events.add(events_module.EVENT_SONAR_OBSTACLE_SEEN)
                self.wasLastReadingBelowThreshold = True
        elif distance > SONAR_OBSTACLE_THRESHOLD + SONAR_OBSTACLE_HYSTERESIS:
            if self.wasLastReadingBelowThreshold:
                events.add(events_module.EVENT_SONAR_OBSTACLE_LOST)
                self.wasLastReadingBelowThreshold = False

