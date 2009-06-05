#!/usr/bin/python


from sonars import *
from buttons import *
from leds import *

import burst
from ..objects import Movable
from burst_consts import ROBOT_DIAMETER


class Robot(Movable):

    debug = burst.options.debug # TODO: Use debug_flags? Or is this a command-line argument?

    def __init__(self, world):
        super(Robot, self).__init__(name='Robot', world=world,
            real_length=ROBOT_DIAMETER)
        self.bumpers = Bumpers(self._world)
        self.chestButton = ChestButton(self._world)
        self.leds = LEDs(world)
        self.leds.turnEverythingOff()
        self.sonars = Sonars(world)
    
    def calc_events(self, events, deferreds):
        self.bumpers.calc_events(events, deferreds)
        self.chestButton.calc_events(events, deferreds)
        self.sonars.calc_events(events, deferreds)
        
    def isHeadMotionInProgress(self):
        return self._world._movecoordinator.isHeadMotionInProgress()

    def isMotionInProgress(self):
        return self._world._movecoordinator.isMotionInProgress()

