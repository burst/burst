#!/usr/bin/python

from burst import events as events_module
import burst


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

    class FSR(Sensor):
        def __init__(self, world, foot, location):
            var = 'Device/SubDeviceList/%sFoot/FSR/%s/Sensor/Value' % (foot, location)
            super(Sensors.FSR, self).__init__(world, var)

    class FootFsrCluster(Sensor):
        def __init__(self, world, foot):
            self._fsrs = []
            for location in [x+y for x in ['Front', 'Rear'] for y in ['Left', 'Right']]:
                self._fsrs.append( Sensors.FSR(world, foot, location) )
        def read(self):
            return min(map(lambda x: x.read(), self._fsrs)) 
        def isPressed(self):
            return self.read() < 1000

    class RightFootFSRs(FootFsrCluster):
        def __init__(self, world):
            super(Sensors.RightFootFSRs, self).__init__(world, 'R')

    class LeftFootFSRs(FootFsrCluster):
        def __init__(self, world):
            super(Sensors.LeftFootFSRs, self).__init__(world, 'L')

    class IntertialSensor(Sensor): # Note: GyrRef, GyrX, AccX...
        def __init__(self, world, var):
            super(Sensors.IntertialSensor, self).__init__(world, var)

    class YAngleIntertialSensor(IntertialSensor):
        def __init__(self, world):
            var = "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value"
            super(Sensors.YAngleIntertialSensor, self).__init__(world, var)

    def __init__(self, world):
#        self.debug = 0
        self.rightFootFSRs = Sensors.RightFootFSRs(world)
        self.leftFootFSRs = Sensors.LeftFootFSRs(world)
        self.yAngleIntertialSensor = Sensors.YAngleIntertialSensor(world)
        self.sensors = [self.rightFootFSRs, self.leftFootFSRs, self.yAngleIntertialSensor]

    def isOnBack(self):
        # If either foot is on the ground, the robot hasn't fallen down.
        if self.rightFootFSRs.isPressed() or self.leftFootFSRs.isPressed():
            return False
        # If neither foot is on the ground, it's up to the inertial sensors:
        return self.yAngleIntertialSensor.read() < -1.0

    def isOnBelly(self):
        # If either foot is on the ground, the robot hasn't fallen down.
        if self.rightFootFSRs.isPressed() or self.leftFootFSRs.isPressed():
            return False
        # If neither foot is on the ground, it's up to the inertial sensors:
        return self.yAngleIntertialSensor.read() > 1.0

    def isFallenDown(self):
        return self.isOnBack() or self.isOnBelly()

    def calc_events(self, events, deferreds):
        # Another frame has passed. Time to poll again anything that requires smoothing:
        for sensor in self.sensors:
            sensor.update()
        # Calculate events:
        if self.isOnBack():
            events.add(events_module.EVENT_FALLEN_DOWN)
            events.add(events_module.EVENT_ON_BACK)
        if self.isOnBelly():
            events.add(events_module.EVENT_FALLEN_DOWN)
            events.add(events_module.EVENT_ON_BELLY)
        self.debug += 1
#        print self.debug, events, self.rightFootFSRs.isPressed(), self.leftFootFSRs.isPressed(), self.yAngleIntertialSensor.read()
#        print map(lambda x: x.read(), self.rightFootFSRs._fsrs), map(lambda x: x.read(), self.leftFootFSRs._fsrs)
