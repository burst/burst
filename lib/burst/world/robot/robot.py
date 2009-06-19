#!/usr/bin/python


from ultrasound import *
from buttons import *
from leds import *
from sensors import *

import burst
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
        self.ultrasound = Ultrasound(world)
        self.hostname = burst.target.robotname # TODO - the whole hostname thing is very convoluted.

    def get_state(self):
        """ return the RobotState - one of gamecontroller.constants.{Initial,Ready,Set,Penalized,Play}RobotState
        """
        # TODO - the interface is fine, the implementation is very cumbersome
        return self._world.gameStatus.myRobotState()

    state = property(get_state)

    def get_status(self):
        return self._world.gameStatus.getMyPlayerStatus()

    status = property(get_status)

    def calc_events(self, events, deferreds):
        self.bumpers.calc_events(events, deferreds)
        self.chestButton.calc_events(events, deferreds)
        self.sensors.calc_events(events, deferreds)
        self.ultrasound.calc_events(events, deferreds)
        # TODO: Fall-down detection should probably be detected here, and not wherever it is now.

    def isHeadMotionInProgress(self):
        return self._world._movecoordinator.isHeadMotionInProgress()

    def isMotionInProgress(self):
        return self._world._movecoordinator.isMotionInProgress()

