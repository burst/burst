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

    debug = burst.options.debug # TODO: Use debug_flags? Or is this a command-line argument?

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
        self.world_x = field.CENTER_FIELD_X
        self.world_y = field.CENTER_FIELD_Y
        self.world_heading = 0.0 # heading towards opponent goal
        self.world_update_time = -200.0 # in 200 seconds we can be in 20m radius - enough to say "I don't know shit"

    def get_state(self):
        """ return the RobotState - one of gamecontroller.constants.{Initial,Ready,Set,Penalized,Play}RobotState
        """
        # TODO - the interface is fine, the implementation is very cumbersome
        return self._world.gameStatus.myRobotState()

    state = property(get_state)

    def get_status(self):
        return self._world.gameStatus.getMyPlayerStatus()

    status = property(get_status)

    def get_jersey(self):
        return self._world.gameStatus.mySettings.playerNumber

    jersey = property(get_jersey)

    def calc_events(self, events, deferreds):
        self.bumpers.calc_events(events, deferreds)
        self.chestButton.calc_events(events, deferreds)
        self.sensors.calc_events(events, deferreds)
        self.sonar.calc_events(events, deferreds)
        # TODO: Fall-down detection should probably be detected here, and not wherever it is now.

