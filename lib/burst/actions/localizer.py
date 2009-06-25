from burst_events import EVENT_WORLD_LOCATION_UPDATED
from burst.behavior import Behavior

class Localizer(Behavior):

    """ Do a repeated search for some landmarks until we can fix our position.
    """

    def __init__(self, actions):
        super(Localizer, self).__init__(actions=actions, name='Localizer')
        self._my_completed = False

    def start(self, targets=None):
        if self.stopped():
            self._targets = targets if targets is not None else [self._world.opposing_lp, self._world.opposing_rp]
        return super(Localizer, self).start()

    def _start(self, firstTime=False):
        # first check if we are already localized. If so return succeed

        # TODO - yellow gate isn't right. We should use "last seen", try to minimize time to localize.
        # TODO - change these to team based

        if not firstTime:
            # we won't need to reregister our bd
            print "ERROR: Don't call Localizer _start directly!"
            import pdb; pdb.set_trace()

        self.log("Starting")

        def onLocationUpdated():
            self.log("got EVENT_WORLD_LOCATION_UPDATED")
            if not self._actions.searcher.stopped():
                self.log("Stopping Searcher (wasn't stopped)")
                self._actions.searcher.stop()
            self.stop()
        self._eventmanager.registerOneShotBD(EVENT_WORLD_LOCATION_UPDATED).onDone(onLocationUpdated)

        self._doSearch()

    def _doSearch(self):
        targets = self._targets
        robot = self._world.robot
        (world_x, world_y, world_heading, world_update_time) = (
            robot.world_x, robot.world_y, robot.world_heading, robot.world_update_time)
        if (world_x and world_y and world_heading and world_update_time
            and not self._world.odometry.movedBetweenTimes(world_update_time, self._world.time)):
            self.log("position is fine right now")
            self.stop()

        # else go forth and localize!
        # we do a little extra work compared to previous versions: we don't just
        # search, we search and search again! we stop only when the EVENT_WORLD_LOCATION_UPDATED
        # actually fires.

        self._actions.search(targets).onDone(self._doSearch)

    def _stop(self):
        self.log("Stopping")
        return self._actions.searcher.stop()

