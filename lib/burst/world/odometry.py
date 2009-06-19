class Odometry(object):
    """
    TODO: should contain estimate of paths walked (x, y, theta)
    for current walk and maybe all walks, to be used by
    Localization class

    Currently holds some functions concerning walks that are computational
    in nature.
    """
    
    def __init__(self, world):
        self._world = world
        self._walks_initiated = []

    def cleanup(self):
        if len(self._walks_initiated) == 0:
            print "Odometry: no movement recorded"
            return
        print "Odometry Summary:"
        print "================="
        for time, description, duration in self._walks_initiated:
            print "%3.1f..%3.1f (%2.1f): %s" % (time, time+duration, duration, description)

    def onWalkInitiated(self, time, description, duration):
        """ record an initiated walk. TODO - anything? """
        # duration is just an estimate, don't count on it (just print it maybe)
        self._walks_initiated.append((time, description, duration))

    def movedBetweenTimes(self, time_start, time_end):
        """ Return True if a movement occured between time_start and time_end,
        and time_start <= time_end.
        """
        # TODO - NOT O(N) PLEASE (using caching maybe)
        if time_start > time_end: return False
        for x in self._walks_initiated:
            t = x[0]
            if time_end >= t >= time_start: return True
        return False

