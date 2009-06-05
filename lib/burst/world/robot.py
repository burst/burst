import burst
from .objects import Movable
from burst_consts import MOTION_FINISHED_MIN_DURATION, ROBOT_DIAMETER, RED, GREEN, BLUE, OFF
from burst_util import BurstDeferred, DeferredList, succeed
from burst import events as events_module



class Sonars(object):

    _var = "extractors/alultrasound/distances"

    class Sonar(object):
        def __init__(self, side, world, index):
            self.side = side
            self.world = world
            self.index = index
        def readDistance(self):
            return self.world.vars[Sonars._var][self.index]

    class LeftSonar(Sonar):
        def __init__(self, world):
            super(Sonars.LeftSonar, self).__init__('Left', world, 0)

    class RightSonar(Sonar):
        def __init__(self, world):
            super(Sonars.RightSonar, self).__init__('Right', world, 1)

    def __init__(self, world):
        world._ultrasound.subscribe('', [500]) # TODO: See if we can lower this without any adverse effects.
        world.addMemoryVars([Sonars._var])
        self.leftSonar = Sonars.LeftSonar(world)
        self.rightSonar = Sonars.RightSonar(world)



class LEDs(object):

    class BaseLED(object):
        def __init__(self, world, side=None):
            self.world = world
            if side != None:
                self.side = side

    class EarLED(BaseLED):
        ''' An abstract class that controls an ear's LEDs. The inheriting classes determine which ear. '''
        def turnOn(self, degreeSet=xrange(0, 360, 36)):
            for degree in degreeSet:
                self.world._leds.on('Ears/Led/%s/%dDeg/Actuator/Value' % (self.side, degree))
        def turnOff(self, degreeSet=xrange(0, 360, 36)):
            for degree in degreeSet:
                self.world._leds.off('Ears/Led/%s/%dDeg/Actuator/Value' % (self.side, degree))

    class LeftEarLED(EarLED):
        def __init__(self, world):
            super(LEDs.LeftEarLED, self).__init__(world, 'Left')

    class RightEarLED(EarLED):
        def __init__(self, world):
            super(LEDs.RightEarLED, self).__init__(world, 'Right')

    class FootLED(BaseLED):
        ''' An abstract class that controls an foot's LEDs. The inheriting classes determine which foot. '''
        def turnOff(self):
            self.world._leds.fadeRGB("%sFootLeds"%self.side, OFF, 0.0)
        def turnOn(self, color):
            self.world._leds.fadeRGB("%sFootLeds"%self.side, color, 0.0)

    class RightFootLED(FootLED):
        def __init__(self, world):
            super(LEDs.RightFootLED, self).__init__(world, 'Right')

    class LeftFootLED(FootLED):
        def __init__(self, world):
            super(LEDs.LeftFootLED, self).__init__(world, 'Left')

    class ChestButtonLED(BaseLED):
        def turnOff(self):
            self.world._leds.fadeRGB("ChestLeds", OFF, 0.0)
        def turnOn(self, color):
            self.world._leds.fadeRGB("ChestLeds", color, 0.0)

    def __init__(self, world):
        self.rightEarLED = LEDs.RightEarLED(world)
        self.leftEarLED = LEDs.LeftEarLED(world)
        self.rightFootLED = LEDs.RightFootLED(world)
        self.leftFootLED = LEDs.LeftFootLED(world)
        self.chestButtonLED = LEDs.ChestButtonLED(world)

    def turnEverythingOff(self):
        for obj in [self.rightEarLED, self.leftEarLED, self.rightFootLED, self.leftFootLED, self.chestButtonLED]:
            obj.turnOff()

    def turnEverythingOn(self):
        for obj in [self.rightEarLED, self.leftEarLED]:
            obj.turnOn()
        for obj in [self.rightFootLED, self.leftFootLED, self.chestButtonLED]:
            obj.turnOn(RED)



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
    ''' In charge of the robot's chest button. Does not include the LED. '''

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
        self.sonars = Sonars(world)
    
    def calc_events(self, events, deferreds):
        self.bumpers.calc_events(events, deferreds)
        self.chestButton.calc_events(events, deferreds)
        
    def isHeadMotionInProgress(self):
        return self._world._movecoordinator.isHeadMotionInProgress()

    def isMotionInProgress(self):
        return self._world._movecoordinator.isMotionInProgress()

