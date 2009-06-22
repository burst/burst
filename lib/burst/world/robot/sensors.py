#!/usr/bin/python

from burst_events import (EVENT_ON_BELLY, EVENT_ON_BACK, EVENT_ON_LEFT_SIDE, EVENT_ON_RIGHT_SIDE, EVENT_PICKED_UP, EVENT_BACK_ON_FEET)
import burst
from burst_consts import FSR_LEG_PRESSED_THRESHOLD, INERTIAL_HISTORY, FSR_HISTORY
from burst_util import running_median

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

    class SmoothedSensor(Sensor):
        def __init__(self, world, var, historyLength):
            super(Sensors.SmoothedSensor, self).__init__(world, var)
            self._historyLength = historyLength
            self.dataRunningMedian = running_median(self._historyLength)
            self.dataRunningMedian.next()
            self.lastRead = None
        def update(self):
            newReading = self._world.vars[self._var]
            if newReading == None:
                return
            # if first reading ever, push another (same) reading to median filter
            if self.lastRead == None:
                for i in range(self._historyLength-1):
                    self.lastRead = self.dataRunningMedian.send(newReading)
            self.lastRead = self.dataRunningMedian.send(newReading)
        def read(self):
            return self.lastRead

    class FootFsrCluster(Sensor):
        def __init__(self, world, foot, historyLength):
            self._fsrs = []
            self._historyLength = historyLength
            self.dataRunningMedian = running_median(self._historyLength)
            self.dataRunningMedian.next()
            self.lastRead = None
            for location in [x+y for x in ['Front', 'Rear'] for y in ['Left', 'Right']]:
                var = 'Device/SubDeviceList/%sFoot/FSR/%s/Sensor/Value' % (foot, location)
                self._fsrs.append( Sensors.Sensor(world, var) )
        def read(self):
            return self.lastRead
        def update(self):
            newReading = sum(map(lambda x: self.transformFSR(x.read()), self._fsrs))
            if newReading == None:
                return
            # if first reading ever, push another (same) reading to median filter
            if self.lastRead == None:
                for i in range(self._historyLength-1):
                    self.lastRead = self.dataRunningMedian.send(newReading)
            self.lastRead = self.dataRunningMedian.send(newReading)
        def transformFSR(self, x):
            if x == 0: return 0
            else: return 1/x
        def isPressed(self):
            return self.read() > FSR_LEG_PRESSED_THRESHOLD

    def __init__(self, world):
        self.rightFootFSRs = Sensors.FootFsrCluster(world, 'R', FSR_HISTORY)
        self.leftFootFSRs = Sensors.FootFsrCluster(world, 'L', FSR_HISTORY)
        self.yAngleInertialSensor = Sensors.SmoothedSensor(world, "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value", INERTIAL_HISTORY)
        self.xAngleInertialSensor = Sensors.SmoothedSensor(world, "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value", INERTIAL_HISTORY)
        self.sensors = [self.rightFootFSRs, self.leftFootFSRs, self.yAngleInertialSensor, self.xAngleInertialSensor]
        self._lastEvent = None

    def calc_events(self, events, deferreds):
        # Another frame has passed. Time to poll again anything that requires smoothing:
        for sensor in self.sensors:
            sensor.update()

        # Calculate events:
        # If neither foot is on the ground, we've fallen:
        newEvent = None
        if (not self.rightFootFSRs.isPressed()) and (not self.leftFootFSRs.isPressed()):
            #print "self.yAngleInertialSensor.read(): ", self.yAngleInertialSensor.read()
            #print "self.xAngleInertialSensor.read(): ", self.xAngleInertialSensor.read()

            if self.yAngleInertialSensor.read() > 0.5:
                newEvent = EVENT_ON_BELLY
            elif self.yAngleInertialSensor.read() < -0.5:
                newEvent = EVENT_ON_BACK
            elif self.xAngleInertialSensor.read() > 0.5:
                newEvent = EVENT_ON_RIGHT_SIDE
            elif self.xAngleInertialSensor.read() < -0.5:
                newEvent = EVENT_ON_LEFT_SIDE
            else:
                # Note: PICKED_UP is basically ignored
                newEvent = EVENT_PICKED_UP
        else:
            if self._lastEvent != None:
                newEvent = EVENT_BACK_ON_FEET

        if newEvent and self._lastEvent != newEvent:
            events.add(newEvent)
            self._lastEvent = newEvent
