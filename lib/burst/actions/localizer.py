from burst_events import EVENT_WORLD_LOCATION_UPDATED
from burst.behavior import Behavior

class Localizer(Behavior):

    """ Do a search for some landmarks until we can fix our position.
    """
    def __init__(self, actions):
        super(Localizer, self).__init__(actions=actions, name='Localizer')

    def _start(self, firstTime=False):
        # first check if we are already localized. If so return succeed
        targets = [self._world.yglp, self._world.ygrp] # TODO - change these to team based
        robot = self._world.robot
        (world_x, world_y, world_heading, world_update_time) = (
            robot.world_x, robot.world_y, robot.world_heading, robot.world_update_time)
        if (world_x and world_y and world_heading and world_update_time
            and not self._world.odometry.movedBetweenTimes(world_update_time, self._world.time)):
            print "Localizer: position is fine right now"
            self.stop()
            if firstTime:
                return self._succeed(self)
            else:
                return self._bd.callOnDone() # return just saves a line

        # else go forth and localize!
        # we do a little extra work compared to previous versions: we don't just
        # search, we search and search again! we stop only when the EVENT_WORLD_LOCATION_UPDATED
        # actually fired.
        self._bd = bd = self._make(self)
        def onLocationUpdated():
            self.stop()
            bd.callOnDone()
        self._eventmanager.registerOneShotBD(EVENT_WORLD_LOCATION_UPDATED).onDone(onLocationUpdated)

        # TODO - yellow gate isn't right. We should use "last seen", try to minimize time to localize.
        self._actions.search(targets).onDone(self._start)

        return bd

