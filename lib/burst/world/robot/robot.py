#!/usr/bin/python


from sonar import *
from buttons import *
from leds import *
from sensors import *

import burst
import burst.field as field
from ..objects import Movable
from burst_consts import ROBOT_DIAMETER

__all__ = ['Robot']

class Robot(Movable):

    debug = burst.options.debug

    def __init__(self, world):
        super(Robot, self).__init__(name='Robot', world=world,
            real_length=ROBOT_DIAMETER)
        self.bumpers = Bumpers(self._world)
        self.chestButton = ChestButton(self._world)
        self.leds = LEDs(world)
        self.leds.turnEverythingOff()
        self.sensors = Sensors(world)
        self.sonar = Sonar(world)
        self.hostname = burst.target.robotname # TODO - the whole hostname thing is very convoluted.

        # These are updated out of object, by Localization.
        self.world_x = field.MIDFIELD_X
        self.world_y = field.MIDFIELD_Y
        self.world_heading = 0.0 # heading towards opponent goal
        self.world_update_time = -200.0 # in 200 seconds we can be in 20m radius - enough to say "I don't know shit"

        #if world.connected_to_webots:
        #    print "WARNING: FALL DETECTION DISABLED!!!! we are on webots, right?"
        #    self.calc_events = self.calc_events_webots

    @property
    def state(self):
        """ return the RobotState - one of gamecontroller.constants.{Initial,Ready,Set,Penalized,Play}RobotState
        """
        # TODO - the interface is fine, the implementation is very cumbersome
        return self._world.gameStatus.myRobotState()

    @property
    def penalized(self):
        return self._world.gameStatus.getMyPlayerStatus().isPenalized()
    
    @property
    def status(self):
        # TODO - doesn't change after configured - so set on configured. not critical.
        return self._world.gameStatus.getMyPlayerStatus()

    @property
    def jersey(self):
        return self._world.gameStatus.mySettings.playerNumber + 1

    @property
    def team_color(self):
        return self._world.gameStatus.mySettings.teamColor

    def calc_events(self, events, deferreds):
        self.bumpers.calc_events(events, deferreds)
        self.chestButton.calc_events(events, deferreds)
        self.sensors.calc_events(events, deferreds)
        self.sonar.calc_events(events, deferreds)
        # TODO: Fall-down detection should probably be detected here, and not wherever it is now.

    def calc_events_webots(self, events, deferreds):
        self.bumpers.calc_events(events, deferreds)
        self.chestButton.calc_events(events, deferreds)
        # sensors disabled - it seems to be buggy, and only required for fall detection anyhow.
        self.sonar.calc_events(events, deferreds)

