#!/usr/bin/python

import sys

from twisted.internet import reactor
from twisted.python import log

foot = lambda foot: ['Device/SubDeviceList/%sFoot/Bumper/%s/Sensor/Value' % (a,foot) for a in ['L', 'R']]

vars = dict(left_foot = foot('Left'), right_foot = foot('Right'),
            chest = ['Device/SubDeviceList/ChestBoard/Button/Sensor/Value'])
ON, OFF = 1.0, 0.0
LIFESPAN_INFINITE = 0

def setIt(con, vars, val):
    for var in vars:
        con.ALMemory.insertData(var, val, LIFESPAN_INFINITE)

def simulateButtonsPress(con, vars):
    setIt(con, vars, ON)
    reactor.callLater(0.5, setIt, con, vars, OFF)
    reactor.callLater(1.0, reactor.stop)

def getvar(name):
    global s, oldstdout
    for k, v in vars.items():
        if k.startswith(name):
            ret = v
            break
    else:
        k, ret = 'chest', vars['chest']
    sys.stdout = oldstdout
    print "Pressing %s" % k
    return ret

if __name__ == '__main__':
    import StringIO
    s=StringIO.StringIO()
    oldstdout  = sys.stdout
    sys.stdout = s
    import player_init
    import pynaoqi
    con  = pynaoqi.getDefaultConnection()
    con.modulesDeferred.addCallback(
        lambda _: simulateButtonsPress(con, getvar(sys.argv[-1].lower()))).addErrback(log.err)
    reactor.run()

