#!/usr/bin/python

from burst import events as events_module
import burst


__all__ = ['Sensors']


class Sensors(object):

    class Sensor(object):
        def read(self):
            pass
        def update(self):
            pass

    class FSR(Sensor):
        _var = 'Device/SubDeviceList/%sFoot/FSR/%s/Sensor/Value'
        def __init__(self, world, foot, location):
            self._world = world
            self._foot = foot
            self._location = location
            world.addMemoryVars( [Sensors.FSR._var % (self._foot, self._location)] )
        def read(self):
            return self._world.vars[Sensors.FSR._var % (self._foot, self._location)]

    class FootFsrCluster(Sensor):
        def __init__(self, world, foot):
            self._fsrs = []
            for location in [x+y for x in ['Front', 'Rear'] for y in ['Left', 'Right']]:
                self._fsrs.append( Sensors.FSR(world, foot, location) )
        def isPressed(self):
            return min(map(lambda x: x.read(), self._fsrs)) < 1000

    class RightFootFSRs(FootFsrCluster):
        def __init__(self, world):
            super(Sensors.RightFootFSRs, self).__init__(world, 'R')

    class LeftFootFSRs(FootFsrCluster):
        def __init__(self, world):
            super(Sensors.LeftFootFSRs, self).__init__(world, 'L')

    class IntertialSensor(Sensor): # Note: GyrRef, GyrX, AccX...
        def __init__(self, world, var):
            self._world = world
            self._var = var
            self._world.addMemoryVars([self._var])
        def read(self):
            return self._world.vars[self._var]

    class YAngleIntertialSensor(IntertialSensor):
        def __init__(self, world):
            super(Sensors.YAngleIntertialSensor, self).__init__(
                world, "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value"
            )
        def update(self):
            pass

    def __init__(self, world):
        self.debug = 0
        self.rightFootFSRs = Sensors.RightFootFSRs(world)
        self.leftFootFSRs = Sensors.LeftFootFSRs(world)
        self.yAngleIntertialSensor = Sensors.YAngleIntertialSensor(world)
        self.sensors = [self.rightFootFSRs, self.leftFootFSRs, self.yAngleIntertialSensor]

    def isOnBack(self):
        return False
        # If either foot is on the ground, the robot hasn't fallen down.
        if self.rightFootFSRs.isPressed() or self.leftFootFSRs.isPressed():
            return False
        # If neither foot is on the ground, it's up to the inertial sensors:
        return self.yAngleIntertialSensor < -1.0

    def isOnBelly(self):
        return False
        # If either foot is on the ground, the robot hasn't fallen down.
        if self.rightFootFSRs.isPressed() or self.leftFootFSRs.isPressed():
            return False
        # If neither foot is on the ground, it's up to the inertial sensors:
        return self.yAngleIntertialSensor > 1.0

    def isFallenDown(self):
        return self.isOnBack() or self.isOnBelly()

    def calc_events(self, events, deferreds):
        self.debug += 1 # TODO: Remove.
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
        print self.debug, events, self.rightFootFSRs.isPressed(), self.leftFootFSRs.isPressed() # TODO: Remove.

#        print map(lambda x: x.read(), self.rightFootFSRs._fsrs), map(lambda x: x.read(), self.leftFootFSRs._fsrs)
