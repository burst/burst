import os, sys, time
import Robot


def setStiffness(stiffness):
	motionProxy = Robot.getMotionProxy()
	TimeInterpolation = 0.05
	motionProxy.setBodyStiffness(stiffness,TimeInterpolation)
	time.sleep(TimeInterpolation)

def slowStraightWalk(distance):
	motionProxy = Robot.getMotionProxy()	
	motionProxy.setWalkArmsConfig( 100.0 * Robot.motion.TO_RAD, 10.0 * Robot.motion.TO_RAD, 30.0 * Robot.motion.TO_RAD, 10.0 * Robot.motion.TO_RAD )
	motionProxy.setWalkArmsEnable(True)
	motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.22, 2.0 )
	motionProxy.setWalkConfig( 0.05, 0.04, 0.04, 0.4, 0.01, 0.00 )
	motionProxy.addWalkStraight( distance, 80)
	motionProxy.walk()
	
def fastStraightWalk(distance):
	motionProxy = Robot.getMotionProxy()
	motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )
	motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )
	motionProxy.addWalkStraight(distance, 25)
	motionProxy.walk()

def initPosition():
	motionProxy = Robot.getMotionProxy()
	joints = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 
		'LElbowRoll', 'LHipYawPitch', 'RHipPitch', 'RHipRoll', 'LHipPitch', 'LHipRoll', 'RKneePitch', 'LKneePitch', 'RAnklePitch', 
		'RAnkleRoll', 'LAnklePitch', 'LAnkleRoll']
	times = len(joints)*[[3]]
	angles = [[50], [0], [10], [35], [50], [0], [0], [-35], [-10], [-40], [0], [-40], [0], [125], [125], [-70], [0], [-70], [0]]
	for i in range(0, len(angles)):
		for j in range(0, len(angles[i])):
			angles[i][j] *= Robot.motion.TO_RAD
	motionProxy.doMove(joints, angles, times, 1)
	
	
def zeroPosition():
	motionProxy = Robot.getMotionProxy()
	motionProxy.gotoBodyAnglesWithSpeed(26*[0.0] , 15, Robot.motion.INTERPOLATION_SMOOTH)


