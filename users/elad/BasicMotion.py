# TODO: Rename to BasicControl, and have every command pass through this module on its way to the Robot?

import os, sys, time
import Robot

def wait(pid):
	motionProxy = Robot.getMotionProxy()
	motionProxy.wait(pid, 0)

def setStiffness(stiffness):
	motionProxy = Robot.getMotionProxy().post
	TimeInterpolation = 0.05
	pid = motionProxy.setBodyStiffness(stiffness,TimeInterpolation)
	time.sleep(TimeInterpolation) # TODO: Should no longer be necessary once I finish the interpreter.
	return pid

def slowStraightWalk(distance):
	motionProxy = Robot.getMotionProxy().post
	motionProxy.setWalkArmsConfig( 100.0 * Robot.motion.TO_RAD, 10.0 * Robot.motion.TO_RAD, 30.0 * Robot.motion.TO_RAD, 10.0 * Robot.motion.TO_RAD )
	motionProxy.setWalkArmsEnable(True)
	motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.22, 2.0 )
	motionProxy.setWalkConfig( 0.05, 0.04, 0.04, 0.4, 0.01, 0.00 )
	motionProxy.addWalkStraight( distance, 80)
	return motionProxy.walk()
	
def fastStraightWalk(distance):
	motionProxy = Robot.getMotionProxy().post
	motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )
	motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )
	motionProxy.addWalkStraight(distance, 25)
	return motionProxy.walk()

def initPosition():
	motionProxy = Robot.getMotionProxy().post
	joints = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 
		'LElbowRoll', 'LHipYawPitch', 'RHipPitch', 'RHipRoll', 'LHipPitch', 'LHipRoll', 'RKneePitch', 'LKneePitch', 'RAnklePitch', 
		'RAnkleRoll', 'LAnklePitch', 'LAnkleRoll']
	times = len(joints)*[[3]]
	angles = [[50], [0], [10], [35], [50], [0], [0], [-35], [-10], [-40], [0], [-40], [0], [125], [125], [-70], [0], [-70], [0]]
	for i in range(0, len(angles)):
		for j in range(0, len(angles[i])):
			angles[i][j] *= Robot.motion.TO_RAD
	return motionProxy.doMove(joints, angles, times, 1)
	
	
def zeroPosition():
	motionProxy = Robot.getMotionProxy().post
	return motionProxy.gotoBodyAnglesWithSpeed(26*[0.0] , 15, Robot.motion.INTERPOLATION_SMOOTH)

"""
def flexLeftArm():
	motionProxy = Robot.getMotionProxy()
	motionProxy.closeHand("LHand")
	

def unflexLeftArm():
	motionProxy = Robot.getMotionProxy()
	motionProxy.openHand("LHand")


def flexRightArm():
	motionProxy = Robot.getMotionProxy()
	motionProxy.closeHand("RHand")
	

def unflexRightArm():
	motionProxy = Robot.getMotionProxy()
	motionProxy.openHand("RHand")
"""

def closeRightHand():
	motionProxy = Robot.getMotionProxy().post
	return motionProxy.closeHand("RHand")


def openRightHand():
	motionProxy = Robot.getMotionProxy().post
	return motionProxy.openHand("RHand")


def closeLeftHand():
	motionProxy = Robot.getMotionProxy().post
	return motionProxy.closeHand("LHand")


def openLeftHand():
	motionProxy = Robot.getMotionProxy().post
	return motionProxy.openHand("LHand")



