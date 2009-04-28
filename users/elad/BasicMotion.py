# TODO: Rename to BasicControl, and have every command pass through this module on its way to the Robot?

import os, sys, time, math
import burst
from burst import burst_exceptions
from burst.burst_exceptions import *


def clearPendingTasks():
    stopWalking()


def wait(pid):
    motionProxy = burst.getMotionProxy()
    motionProxy.wait(pid, 0)


def setStiffness(stiffness):
    motionProxy = burst.getMotionProxy().post
    pid = motionProxy.setBodyStiffness(stiffness)
    # Dirty hack:
    if stiffness == 0.0:
        stopWalking()
    return pid


def slowStraightWalk(distance):
    motionProxy = burst.getMotionProxy().post
    motionProxy.setWalkArmsConfig( 100.0 * burst.motion.TO_RAD, 10.0 * burst.motion.TO_RAD, 30.0 * burst.motion.TO_RAD, 10.0 * burst.motion.TO_RAD )
    motionProxy.setWalkArmsEnable(True)
    motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.22, 2.0 )
    motionProxy.setWalkConfig( 0.05, 0.04, 0.04, 0.4, 0.01, 0.00 )
    motionProxy.addWalkStraight( distance, 80)
    return motionProxy.walk()

    
def fastStraightWalk(distance):
    motionProxy = burst.getMotionProxy().post
    motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )
    motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )
    motionProxy.addWalkStraight(distance, 25)
    return motionProxy.walk()


def initPosition():
    motionProxy = burst.getMotionProxy().post
    joints = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 
        'LElbowRoll', 'LHipYawPitch', 'RHipPitch', 'RHipRoll', 'LHipPitch', 'LHipRoll', 'RKneePitch', 'LKneePitch', 'RAnklePitch', 
        'RAnkleRoll', 'LAnklePitch', 'LAnkleRoll']
    times = len(joints)*[[3]]
    angles = [[50], [0], [10], [35], [50], [0], [0], [-35], [-10], [-40], [0], [-40], [0], [125], [125], [-70], [0], [-70], [0]]
    for i in range(0, len(angles)):
        for j in range(0, len(angles[i])):
            angles[i][j] *= burst.motion.TO_RAD
    return motionProxy.doMove(joints, angles, times, 1)
    
    
def zeroPosition():
    motionProxy = burst.getMotionProxy().post
    return motionProxy.gotoBodyAnglesWithSpeed(26*[0.0] , 15, burst.motion.INTERPOLATION_SMOOTH)


def flexLeftArm():
    motionProxy = burst.getMotionProxy().post
    x = motionProxy.getChainAngles("LArm")
    x[3] = -math.pi
    return motionProxy.post.gotoChainAngles("LArm", x, 3.0, 1)


def unflexLeftArm():
    motionProxy = burst.getMotionProxy().post
    x = motionProxy.getChainAngles("LArm")
    x[3] = math.pi
    return motionProxy.post.gotoChainAngles("LArm", x, 3.0, 1)


def flexRightArm():
    motionProxy = burst.getMotionProxy().post
    x = motionProxy.getChainAngles("RArm")
    x[3] = math.pi
    return motionProxy.post.gotoChainAngles("RArm", x, 3.0, 1)
    

def unflexRightArm():
    motionProxy = burst.getMotionProxy().post
    x = motionProxy.getChainAngles("RArm")
    x[3] = -math.pi
    return motionProxy.post.gotoChainAngles("RArm", x, 3.0, 1)


def closeRightHand():
    motionProxy = burst.getMotionProxy().post
    return motionProxy.closeHand("RHand")


def openRightHand():
    motionProxy = burst.getMotionProxy().post
    return motionProxy.openHand("RHand")


def closeLeftHand():
    motionProxy = burst.getMotionProxy().post
    return motionProxy.closeHand("LHand")


def openLeftHand():
    motionProxy = burst.getMotionProxy().post
    return motionProxy.openHand("LHand")


def stopWalking():
    motionProxy = burst.getMotionProxy().post
    motionProxy.clearFootsteps()
    return None


def killAllTasks():
    # Deprecated.
    motionProxy = burst.getMotionProxy()
    motionProxy.killAll()
    #motionProxy.setBalanceMode(1)
    #motionProxy.setSupportMode(0)
    return None


def addWalkStraight(distance, samples):
    motionProxy = burst.getMotionProxy().post
    return motionProxy.addWalkStraight(distance, samples)


def turn(degrees):
    motionProxy = burst.getMotionProxy().post
    motionProxy.addTurn(float(degrees), 60)
    return motionProxy.walk()
    

def addTurn(degrees):
    motionProxy = burst.getMotionProxy().post
    motionProxy.addTurn(float(degrees), 60)


def shoot():
    import Shoot
    Shoot.do()


def getUpFromFront():
    import GetUpFromFront
    GetUpFromFront.do()


def getUpFromBack():
    import GetUpFromBack
    GetUpFromBack.do()


def isOnBack():
    memory = burst.getMemoryProxy()
    y = memory.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",0)
    return y < -1.0


def isOnBelly():
    memory = burst.getMemoryProxy()
    y = memory.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",0)
    return y > 1.0


def isSafeToGetUp():
    memory = burst.getMemoryProxy()
    x = memory.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",0)
    return abs(x) < 0.5


def getUp():
    print "a"
    if isOnBelly():
        print "b"
        if isSafeToGetUp():
            getUpFromFront()
        else:
            print "onbelly, unsafe"
            raise UnsafeToGetUpException
    elif isOnBack():
        if isSafeToGetUp():
            getUpFromBack()
        else:
            print "onback, unsafe"
            raise UnsafeToGetUpException
    else:
        raise NotLyingDownException


def headStiffnessOn():
    motionProxy = burst.getMotionProxy().post
    motionProxy.setChainStiffness('Head', 1.0, 0)
    
    
def headStiffnessOff():
    motionProxy = burst.getMotionProxy().post
    motionProxy.setChainStiffness('Head', 0.0, 0)


def moveHead(x, y):
    motionProxy = burst.getMotionProxy()
    headStiffnessOn()
    motionProxy.gotoChainAngles('Head', [float(x), float(y)], 1, 1)


# -2, -1?, -0.4, 0


