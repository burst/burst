# Note: We use world.motion, but don't construct it so no need to import

def interval_overlap((t1, t2), (T1, T2)):
    """ special case of interval computation (so it is left here and
    not put in burst_util): The first interval is known and ordered,
    the second is ordered but might be open ended (T2 not known)
    """
    # assume t1<t2, T1<T2
    # Better way then enumerating the cases?
    if T2 is None:
        # T1 is open ended (start time, no end time)
        return ((t1 <= T1 <= t2)
            or  (T1 <= t1))
    return (    (T1 <= t1 <= T2)
            or  (T1 <= t2 <= T2)
            or  (t1 <= T1 <= t2))

class Motion(object):

    def __init__(self, start_time, estimated_duration, description):
        self.description = description
        self.start_time = start_time
        self.end_time = None # set by onWalkComplete
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

    # World/MainEventLoop API

    def cleanup(self):
        if len(self._walks_initiated) == 0:
            print "Odometry: no movement recorded"
            return
        print "Odometry Summary:"
        print "================="
        for motion in self._walks_initiated:
            start, end, description, estimated_duration = (
                motion.start_time, motion.end_time, motion.description, motion.estimated_duration)
            duration = end - start
            # TODO - real duration, from the end event, or using a deferred (onDone for odometry)
            print "%3.1f..%3.1f (%2.1f/est %2.1f): %s" % (start, end, duration, estimated_duration, description)

    # Actions API

    def onWalkInitiated(self, motion):
        """ record an initiated walk. TODO - anything? """
        # duration is just an estimate, don't count on it (just print it maybe)
        self._walks_initiated.append(motion)

    def onWalkComplete(self, motion):
        if motion is None:
            import pdb; pdb.set_trace()
        motion.end_time = self._world.time
        #assert(motion in self._walks_initiated)

    # Behavior API

    def movedBetweenTimes(self, time_start, time_end):
        """ Return True if a movement occured between time_start and time_end,
        and time_start <= time_end.
        """
        # TODO - NOT O(N) PLEASE (using caching maybe)
        # TODO - FIXME - this is not correct. doesn't account for a walk that starts before and end after or during.
        if time_start > time_end: return False
        return any(interval_overlap((time_start, time_end),
                    (motion.start_time, motion.end_time)) for motion in self._walks_initiated)

