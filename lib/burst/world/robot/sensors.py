#!/usr/bin/python

import burst_events
import burst
from burst_consts import FSR_LEG_PRESSED_THRESHOLD

__all__ = ['Sensors']


class Sensors(object):

    class Sensor(object):
        def __init__(self, world, var):
            self._world = world
            self._var = var
            world.addMemoryVars([var])
        def read(self):
            return self._world.vars[self._var]
        def update(self):
            pass

    class FootFsrCluster(Sensor):
        def __init__(self, world, foot):
            self._fsrs = []
            for location in [x+y for x in ['Front', 'Rear'] for y in ['Left', 'Right']]:
                var = 'Device/SubDeviceList/%sFoot/FSR/%s/Sensor/Value' % (foot, location)
                self._fsrs.append( Sensors.Sensor(world, var) )
        def read(self):
            return sum(map(lambda x: self.transformFSR(x.read()), self._fsrs))
        def transformFSR(self, x):
            if x == 0:
                return 0
            else:
                return 1/x
        def isPressed(self):
            return self.read() > FSR_LEG_PRESSED_THRESHOLD

    class InertialSensor(Sensor): # Note: GyrRef, GyrX, AccX...
        def __init__(self, world, var):
            super(Sensors.InertialSensor, self).__init__(world, var)

    class YAngleInertialSensor(InertialSensor):
        def __init__(self, world):
            var = "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value"
            super(Sensors.YAngleInertialSensor, self).__init__(world, var)

    def __init__(self, world):
#        self.debug = 0
        self.rightFootFSRs = Sensors.FootFsrCluster(world, 'R')
        self.leftFootFSRs = Sensors.FootFsrCluster(world, 'L')
        self.yAngleInertialSensor = Sensors.YAngleInertialSensor(world)
        self.sensors = [self.rightFootFSRs, self.leftFootFSRs, self.yAngleInertialSensor]

    def isFallenDown(self):
        # If neither foot is on the ground and the inertial sensor says we're down:
        return (not self.rightFootFSRs.isPressed()) and (not self.leftFootFSRs.isPressed()) and \
                abs(self.yAngleInertialSensor.read()) > 1.0

    def calc_events(self, events, deferreds):
        # Another frame has passed. Time to poll again anything that requires smoothing:
        for sensor in self.sensors:
            sensor.update()
        # Calculate events:
        if self.isFallenDown():
            events.add(burst_events.EVENT_FALLEN_DOWN)
            if self.yAngleInertialSensor.read() > 1.0:
                events.add(burst_events.EVENT_ON_BELLY)
            else: #if self.yAngleInertialSensor.read() < -1.0:
                events.add(burst_events.EVENT_ON_BACK)
        
#        self.debug += 1
#        print self.debug, events, self.rightFootFSRs.isPressed(), self.leftFootFSRs.isPressed(), self.yAngleInertialSensor.read()
#        print map(lambda x: x.read(), self.rightFootFSRs._fsrs), map(lambda x: x.read(), self.leftFootFSRs._fsrs)
