import burst
from .objects import Movable
from burst_consts import MOTION_FINISHED_MIN_DURATION, ROBOT_DIAMETER
from burst_util import BurstDeferred, DeferredList, succeed
from burst import events as events_module



class LEDs(object):

    class EarLED(object):
        '''
        An abstract class that controls an ear's LEDs. The inheriting classes determine which ear.
        '''
        def __init__(self, side, world):
            self.side = side
            self.world = world
        def turnOn(self, degreeSet=xrange(0, 360, 36)):
            for degree in degreeSet:
                self.world._leds.on('Ears/Led/%s/%dDeg/Actuator/Value' % (self.side, degree))
        def turnOff(self, degreeSet=xrange(0, 360, 36)):
            for degree in degreeSet:
                self.world._leds.off('Ears/Led/%s/%dDeg/Actuator/Value' % (self.side, degree))

    class LeftEarLED(EarLED):
        def __init__(self, world):
            super(LEDs.LeftEarLED, self).__init__('Left', world)

    class RightEarLED(EarLED):
        def __init__(self, world):
            super(LEDs.RightEarLED, self).__init__('Right', world)

    def __init__(self, world):
        self.rightEarLED = LEDs.RightEarLED(world)
        self.leftEarLED = LEDs.LeftEarLED(world)

    def turnEverythingOff(self):
        for obj in [self.rightEarLED, self.leftEarLED]:
            obj.turnOff()

    def turnEverythingOn(self):
        for obj in [self.rightEarLED, self.leftEarLED]:
            obj.turnOn()



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
            events.add(events_module.EVENT_LEFT_BUMPER_PRESSED)
        if not self.rightBumperPressed and right:
            events.add(events_module.EVENT_RIGHT_BUMPER_PRESSED)
        self.leftBumperPressed, self.rightBumperPressed = left, right


class ChestButton(object):

    def __init__(self, world):
        self._world = world
        self._vars = ['Device/SubDeviceList/ChestBoard/Button/Sensor/Value']
        self._world.addMemoryVars(self._vars)
        self.oldVal = 0.0

    def calc_events(self, events, deferreds):
        newVal, = self._world.getVars(self._vars)
        if newVal > 0.5 and self.oldVal < 0.5:
            events.add(events_module.EVENT_CHEST_BUTTON_PRESSED)
        if newVal < 0.5 and self.oldVal > 0.5:
            events.add(events_module.EVENT_CHEST_BUTTON_RELEASED)
        self.oldVal = newVal


class Robot(Movable):

    debug = burst.options.debug

    def __init__(self, world):
        super(Robot, self).__init__(name='Robot', world=world,
            real_length=ROBOT_DIAMETER)
        self.bumpers = Bumpers(self._world)
        self.chestButton = ChestButton(self._world)
        self.leds = LEDs(world)
        self.leds.turnEverythingOff()
    
    def calc_events(self, events, deferreds):
        self.bumpers.calc_events(events, deferreds)
        self.chestButton.calc_events(events, deferreds)
        
    def isHeadMotionInProgress(self):
        return self._world._movecoordinator.isHeadMotionInProgress()

    def isMotionInProgress(self):
        return self._world._movecoordinator.isMotionInProgress()

