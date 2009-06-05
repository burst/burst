#!/usr/bin/python


from burst_consts import RED, GREEN, BLUE, OFF


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
