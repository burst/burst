from burst_events import EVENT_WORLD_LOCATION_UPDATED
from burst.behavior import Behavior

class Localizer(Behavior):

    """ Do a repeated search for some landmarks until we can fix our position.
    """

    def __init__(self, actions):
        super(Localizer, self).__init__(actions=actions, name='Localizer')
        self._my_completed = False

    def _start(self, firstTime=False):
        # first check if we are already localized. If so return succeed

        # TODO - yellow gate isn't right. We should use "last seen", try to minimize time to localize.
        # TODO - change these to team based

        self.log("Starting")

        targets = [self._world.yglp, self._world.ygrp]

        robot = self._world.robot
        (world_x, world_y, world_heading, world_update_time) = (
            robot.world_x, robot.world_y, robot.world_heading, robot.world_update_time)
        if (world_x and world_y and world_heading and world_update_time
            and not self._world.odometry.movedBetweenTimes(world_update_time, self._world.time)):
            self.log("position is fine right now")
            self.stop()
            self.callOnDone()

        # else go forth and localize!
        # we do a little extra work compared to previous versions: we don't just
        # search, we search and search again! we stop only when the EVENT_WORLD_LOCATION_UPDATED
        # actually fires.
        def onLocationUpdated():
            self.log("got EVENT_WORLD_LOCATION_UPDATED")
            self.stop()
            if not self._actions.searcher.stopped():
                self.log("Stopping Searcher (wasn't stopped)")
                self._actions.searcher.stop()
            self.callOnDone()
        self._eventmanager.registerOneShotBD(EVENT_WORLD_LOCATION_UPDATED).onDone(onLocationUpdated)

        self._actions.search(targets).onDone(self._start)

    def _stop(self):
        self.log("Stopping")

