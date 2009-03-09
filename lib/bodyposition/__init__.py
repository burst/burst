#!/usr/bin/python

import burst
from burst import ALBroker, ALProxy
import motion

def split_camel(st):
    ret = []
    s = 0
    upper = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    it = enumerate(st)
    it.next()
    for i, c in it:
        if c in upper:
            ret.append(st[s:i])
            s = i
    ret.append(st[s:])
    return ret

def camel_to_under(s):
    ws = split_camel(s)
    return '_'.join([x.lower() for x in ws])

class BodyPosition(object):
    # Create all the device names for ALMemory, and short names for easy access
    feet_parts =  ['FrontLeft', 'FrontRight', 'RearLeft', 'RearRight']
    fsr_parts = [('LFoot',y) for y in feet_parts] + [('RFoot', y) for y in feet_parts]
    FSR = [
    ((x,y), 'Device/SubDeviceList/%s/FSR/%s/Sensor/Value' % (x,y))
        for x,y in fsr_parts]
    INERTIAL = [(y, 'Device/SubDeviceList/InertialSensor/%s/Sensor/Value' % y)
        for y in ['GyrX', 'GyrY', 'AccX', 'AccY', 'AccZ', 'AngleX', 'AngleY']]
    _fsr_full = [x[1] for x in FSR]
    _fsr_short = [x[0] for x in FSR]
    _inertial_full = [x[1] for x in INERTIAL]
    _inertial_short = [x[0] for x in INERTIAL]
    _both_full = _fsr_full + _inertial_full
    _short_to_full_name = FSR + INERTIAL
    _short_to_full_name_d = dict(_short_to_full_name)
    _full_to_short_name_d = dict([(y,x) for x,y in _short_to_full_name])

    def __init__(self, broker=None, ip=burst.ip, port=burst.port):
        self._broker = broker
        if self._broker is None:
            self._broker = ALBroker("pybroker", "127.0.0.1", 9999, ip, port)
        self._mem = ALProxy("ALMemory")
        self._d = dict([(x, 0.0) for x in self._short_to_full_name_d.values()])
        
    def updateFSR(self):
        for k in self._fsr_full:
            self._d[k] = self._mem.getData(k, 0)
            
    def updateInertial(self):
        for k in self._inertial_full:
            self._d[k] = self._mem.getData(k, 0)
    def computeStates(self):
        pass
    def update(self):
        self.updateFSR()
        self.updateInertial()
        self.computeStates()
    def get_fsr(self):
        return self._fsr
    def get_inertial(self):
        return self._inertial
    fsr = property(get_fsr)
    inertial = property(get_inertial)

    @classmethod
    def short(self, n):
        return self._full_to_short_name_d[n]

    @classmethod
    def full(self, n):
        return self._short_to_full_name_d[n]

    def __str__(self):
        return '\n'.join(
             ['%25s: %8.2f (%2.6f)' % (self.short(k), self._d[k], 1.0/self._d[k]) for k in self._fsr_full]
             + ['%25s: %8.2f' % (self.short(k), self._d[k]) for k in self._inertial_full])
        
    def pprint(self):
        print str(self)

def addPropertiesToBodyPosition():
    for short, camel in [(xy, xy[0]+xy[1]) for xy in BodyPosition._fsr_short] + [(x,x) for x in BodyPosition._inertial_short]:
        attr = camel_to_under(camel)
        full = BodyPosition.full(short)
        setattr(BodyPosition, attr, property(lambda self,attr=attr,full=full:
            self._d[full]))

addPropertiesToBodyPosition()

def read_until_ctrl_c():
    from time import sleep
    bp = BodyPosition()
    try:
        while True:
            bp.update()
            bp.pprint()
            sleep(0.1)
    except KeyboardInterrupt:
        print "ctrl-c pressed, exiting..."

if __name__ == '__main__':
    read_until_ctrl_c()

