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

    def movedBetweenTimes(self, t1, t2):
        """ Return True if a movement occured between t1 and t2 (and t2>=t1)
        Uses self._world.movecoordinator which contains some queues and stuff
        """
        # TODO - NOT O(N) PLEASE (using caching maybe)
        if t1 > t2: return False
        for x in self._world._movecoordinator._initiated:
            t = x[0]
            if t2 >= t >= t1: return True
        return False

