#!/usr/bin/python

from burst import events as events_module
import burst


__all__ = ['Sensors']


class Sensors(object):

    class FSR(object):
        _var = 'Device/SubDeviceList/%sFoot/FSR/%s/Sensor/Value'
        def __init__(self, world, foot, location):
            self._world = world
            self._foot = foot
            self._location = location
            world.addMemoryVars( [Sensors.FSR._var % (self._foot, self._location)] )
        def read(self):
            return self._world.vars[Sensors.FSR._var % (self._foot, self._location)]

    class FootFsrCluster(object):
        def __init__(self, world, foot):
            self._fsrs = []
            for location in [x+y for x in ['Front', 'Rear'] for y in ['Left', 'Right']]:
                self._fsrs.append( Sensors.FSR( world, foot, location) )

    class RightFootFSRs(FootFsrCluster):
        def __init__(self, world):
            super(Sensors.RightFootFSRs, self).__init__(world, 'R')

    class LeftFootFSRs(FootFsrCluster):
        def __init__(self, world):
            super(Sensors.LeftFootFSRs, self).__init__(world, 'L')

    def __init__(self, world):
        self.rightFootFSRs = Sensors.RightFootFSRs(world)
        self.leftFootFSRs = Sensors.LeftFootFSRs(world)
        self.footFSRs = [self.rightFootFSRs, self.leftFootFSRs]

    def calc_events(self, events, deferreds):
        pass
#        print map(lambda x: x.read(), self.rightFootFSRs._fsrs), map(lambda x: x.read(), self.leftFootFSRs._fsrs)
