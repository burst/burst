#!/usr/bin/python


import burst_events

__all__ = ['Bumpers', 'ChestButton']


class Bumpers(object):

    def __init__(self, world):
        self._world = world
        self._vars = ['Device/SubDeviceList/%sFoot/Bumper/%s/Sensor/Value' % (a,b) for a in ['L', 'R'] for b in ['Left', 'Right']]
        self._world.addMemoryVars(self._vars)
        self.leftBumperPressed, self.rightBumperPressed = False, False

    def calc_events(self, events, deferreds):
        (self.leftBumperRightSensor, self.leftBumperLeftSensor, self.rightBumperLeftSensor,
            self.rightBumperRightSensor) = self._world.getVars(self._vars)
        left, right = ((self.leftBumperRightSensor+self.leftBumperLeftSensor)/2.0 > 0.5,
            (self.rightBumperLeftSensor+self.rightBumperRightSensor)/2.0 > 0.5)
        if not self.leftBumperPressed and left:
            events.add(burst_events.EVENT_LEFT_BUMPER_PRESSED)
        if not self.rightBumperPressed and right:
            events.add(burst_events.EVENT_RIGHT_BUMPER_PRESSED)
        self.leftBumperPressed, self.rightBumperPressed = left, right



class ChestButton(object):
    ''' In charge of the robot's chest button. Does not include the LED. '''

    def __init__(self, world):
        self._world = world
        self._vars = ['Device/SubDeviceList/ChestBoard/Button/Sensor/Value']
        self._world.addMemoryVars(self._vars)
        self.oldVal = 0.0

    def calc_events(self, events, deferreds):
        newVal, = self._world.getVars(self._vars)
        if newVal > 0.5 and self.oldVal < 0.5:
            events.add(burst_events.EVENT_CHEST_BUTTON_PRESSED)
        if newVal < 0.5 and self.oldVal > 0.5:
            events.add(burst_events.EVENT_CHEST_BUTTON_RELEASED)
        self.oldVal = newVal
