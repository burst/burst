from events import EVENT_FALLEN_DOWN, EVENT_ON_BELLY, EVENT_ON_BACK

SMOOTHING_FACTOR = 5

class FalldownDetector(object):
    """ Detecting / Storing robot fall down state
    """
    # As the data is somewhat noisy - y values of 4.83 surrounded by 0.02, 0.05 and 0.04 - I've 
    # added a little bit of smoothing.
    
    def __init__(self, world):
        self._world = world
        self._var = "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value"
        self._world.addMemoryVars([self._var])
        self.ys = [0.0 for i in xrange(SMOOTHING_FACTOR)]

    def hasFallenDown(self):
        return self.isOnBack() or self.isOnBelly()

    def calc_events(self, events, deferreds):
        self.ys = self.ys[1:] + [self._world.vars[self._var]]
        self.y = sorted(self.ys)[len(self.ys)/2]
#        print "y:", str(self.y)
        self._on_back = self.y < -1.0
        self._on_belly = self.y > 1.0

        # Check if the robot has fallen down. If it has, fire the appropriate event.
        # TODO: Maybe I should fire FALLEN_DOWN only the first time around (but keep ON_BELLY and ON_BACK as they are)?
        if self.hasFallenDown():
            events.add(EVENT_FALLEN_DOWN)
            if self.isOnBelly():
                events.add(EVENT_ON_BELLY)
            if self.isOnBack():
                events.add(EVENT_ON_BACK)

    def isOnBack(self):
        return self._on_back

    def isOnBelly(self):
        return self._on_belly

