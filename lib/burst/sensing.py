import burst
from burst.consts import *


# Cached values. They serve to use the memory module less, as it might be a bit slow.
cachedY = None

# TODO: Should I cache memory, or is that just a splendid way to create a pitfall where people
# accidentally import this module before they import the /burst/ module, and so an error is fired when memory is first accessed?


def hasFallenDown():
    return isOnBack() or isOnBelly()


def isOnBack(useCachedValue=False):
    if useCachedValue and not cachedY == None:
        y = cachedY
    else:
        memory = burst.getMemoryProxy()
        y = memory.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",0)
    return y < -1.0


def isOnBelly(useCachedValue=False):
    if useCachedValue and not cachedY == None:
        y = cachedY
    else:
        memory = burst.getMemoryProxy()
        y = memory.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",0)
    return y > 1.0
