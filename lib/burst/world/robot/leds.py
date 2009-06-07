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
                self.world._leds.post.on('Ears/Led/%s/%dDeg/Actuator/Value' % (self.side, degree))
        def turnOff(self, degreeSet=xrange(0, 360, 36)):
            for degree in degreeSet:
                self.world._leds.post.off('Ears/Led/%s/%dDeg/Actuator/Value' % (self.side, degree))

    class LeftEarLED(EarLED):
        def __init__(self, world):
            super(LEDs.LeftEarLED, self).__init__(world, 'Left')

    class RightEarLED(EarLED):
        def __init__(self, world):
            super(LEDs.RightEarLED, self).__init__(world, 'Right')

    class FootLED(BaseLED):
        ''' An abstract class that controls an foot's LEDs. The inheriting classes determine which foot. '''
        def turnOff(self):
            self.world._leds.post.fadeRGB("%sFootLeds"%self.side, OFF, 0.0)
        def turnOn(self, color):
            self.world._leds.post.fadeRGB("%sFootLeds"%self.side, color, 0.0)

    class RightFootLED(FootLED):
        def __init__(self, world):
            super(LEDs.RightFootLED, self).__init__(world, 'Right')

    class LeftFootLED(FootLED):
        def __init__(self, world):
            super(LEDs.LeftFootLED, self).__init__(world, 'Left')

    class EyeLED(BaseLED):
        def turnOff(self):
            for color in ['Red', 'Green', 'Blue']:
                for deg in xrange(0, 360, 45):
                    self.world._leds.post.off("Face/Led/%s/%s/%dDeg/Actuator/Value"%(color, self.side, deg))
        def turnOn(self, color):
            colors = []
            for rgbColor, colorName in zip([RED, GREEN, BLUE], ['Red', 'Green', 'Blue']):
                if rgbColor & color != 0:
                    for deg in xrange(0, 360, 45):
                        self.world._leds.post.on("Face/Led/%s/%s/%dDeg/Actuator/Value"%(colorName, self.side, deg))
                else:
                    for deg in xrange(0, 360, 45):
                        self.world._leds.post.off("Face/Led/%s/%s/%dDeg/Actuator/Value"%(colorName, self.side, deg))

    class RightEyeLED(EyeLED):
        def __init__(self, world):
            super(LEDs.RightEyeLED, self).__init__(world, 'Right')

    class LeftEyeLED(EyeLED):
        def __init__(self, world):
            super(LEDs.LeftEyeLED, self).__init__(world, 'Left')

    class ChestButtonLED(BaseLED):
        def turnOff(self):
            self.world._leds.post.fadeRGB("ChestLeds", OFF, 0.0)
        def turnOn(self, color):
            self.world._leds.post.fadeRGB("ChestLeds", color, 0.0)

    def __init__(self, world):
        self.rightEarLED = LEDs.RightEarLED(world)
        self.leftEarLED = LEDs.LeftEarLED(world)
        self.rightFootLED = LEDs.RightFootLED(world)
        self.leftFootLED = LEDs.LeftFootLED(world)
        self.chestButtonLED = LEDs.ChestButtonLED(world)
        self.rightEyeLED = LEDs.RightEyeLED(world)
        self.leftEyeLED = LEDs.LeftEyeLED(world)

    def turnEverythingOff(self):
        for obj in [self.rightEarLED, self.leftEarLED, self.rightFootLED, self.leftFootLED, self.chestButtonLED, self.rightEyeLED, self.leftEyeLED]:
            obj.turnOff()

    def turnEverythingOn(self): # For debugging purposes only. Not all-encompassing.
        for obj in [self.rightEarLED, self.leftEarLED]:
            obj.turnOn()
        for obj in [self.rightFootLED, self.leftFootLED, self.chestButtonLED]:
            obj.turnOn(RED)

