# Note: We use world.motion, but don't construct it so no need to import

class Motion(object):

    def __init__(self, start_time, estimated_duration, description):
        self.description = description
        self.start_time = start_time
        self.estimated_duration = estimated_duration


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
        for motion in self._walks_initiated:
            time, description, duration = motion.start_time, motion.description, motion.estimated_duration
            # TODO - real duration, from the end event, or using a deferred (onDone for odometry)
            print "%3.1f..%3.1f (%2.1f): %s" % (time, time+duration, duration, description)

    def onWalkInitiated(self, motion):
        """ record an initiated walk. TODO - anything? """
        # duration is just an estimate, don't count on it (just print it maybe)
        self._walks_initiated.append(motion)

    def movedBetweenTimes(self, time_start, time_end):
        """ Return True if a movement occured between time_start and time_end,
        and time_start <= time_end.
        """
        # TODO - NOT O(N) PLEASE (using caching maybe)
        # TODO - FIXME - this is not correct. doesn't account for a walk that starts before and end after or during.
        if time_start > time_end: return False
        for motion in self._walks_initiated:
            t = motion.start_time
            if time_end >= t >= time_start: return True
        return False

