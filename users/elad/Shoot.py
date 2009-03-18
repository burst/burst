# TODO: This entire file looks like shit.

import time
import Robot

def do():
	broker = Robot.getBroker()	motionProxy = Robot.getMotionProxy()

	# Define The Initial Position
	kneeAngle = 60.0 * Robot.motion.TO_RAD
	torsoAngle = 0.0 * Robot.motion.TO_RAD
	wideAngle = -3.0 * Robot.motion.TO_RAD

	#Get the Number of Joints
	NumJoints = len(motionProxy.getBodyJointNames())

	# Define The Initial Position
	InitialPosition = [0.0 * Robot.motion.TO_RAD, 0.0 * Robot.motion.TO_RAD,
		 120.0 * Robot.motion.TO_RAD, 15.0 * Robot.motion.TO_RAD, -80.0 * Robot.motion.TO_RAD, -80.0 * Robot.motion.TO_RAD, 0.0 * Robot.motion.TO_RAD,0.0,
		 0.0, wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, -wideAngle, 
		 0.0, -wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, wideAngle, 
		 120.0 * Robot.motion.TO_RAD, -15.0 * Robot.motion.TO_RAD, 80.0 * Robot.motion.TO_RAD, 80.0 * Robot.motion.TO_RAD, 0.0 * Robot.motion.TO_RAD, 0.0]

	# Set balancer Off to allow full control of Nao joints
	motionProxy.setBalanceMode(Robot.motion.BALANCE_MODE_OFF)
	# Send angles through a smooth interpolation (max motors speed: 30%)
	motionProxy.gotoBodyAnglesWithSpeed(InitialPosition ,30, Robot.motion.INTERPOLATION_SMOOTH)

	motionProxy.setSupportMode(Robot.motion.SUPPORT_MODE_DOUBLE_RIGHT)
	# Set the Balancer in Automatique Mode
	motionProxy.setBalanceMode(Robot.motion.BALANCE_MODE_AUTO)

	# Go to Simple Support RIGHT
	motionProxy.setSupportMode(Robot.motion.SUPPORT_MODE_RIGHT)
	time.sleep(3)

	#####################################################################
	#####################################################################
	InterpolationTimeForThisSection = 0.4 #In seconds

	#~ # Bend The Torso Forward
	Rx = 0.2
	Ry = 0.0
	motionProxy.post.gotoTorsoOrientation(Rx,Ry,InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Raise The LEFT_LEG
	ActualPosition = motionProxy.getPosition("LLeg", Robot.motion.SPACE_SUPPORT_LEG)
	X = -0.01
	Y = 0.00
	Z = 0.03
	wX = 0.0
	wY = 0.0
	wZ = 0.0
	Cmd = [ActualPosition[0]+X, ActualPosition[1]+Y, ActualPosition[2]+Z, ActualPosition[3]+wX, ActualPosition[4]+wY, ActualPosition[5]+wZ]
	motionProxy.gotoPosition("LLeg", Robot.motion.SPACE_SUPPORT_LEG, Cmd, Robot.motion.AXIS_MASK_ALL, InterpolationTimeForThisSection, Robot.motion.INTERPOLATION_SMOOTH) 

	#####################################################################
	#####################################################################
	InterpolationTimeForThisSection = 0.4 #In seconds

	# Bend The Torso Forward
	Rx = 0.2
	Ry = 0.4
	motionProxy.post.gotoTorsoOrientation(Rx,Ry,InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Move Head
	motionProxy.post.gotoAngle('HeadPitch', -0.4, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Move Arms
	Id3 = motionProxy.post.gotoAngle('LShoulderPitch', 70 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	Id4 = motionProxy.post.gotoAngle('LElbowRoll', -80 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	Id5 = motionProxy.post.gotoAngle('RShoulderPitch', 120 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	Id6 = motionProxy.post.gotoAngle('RElbowRoll', 0 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Move The LEFT_LEG Backward
	X = -0.04
	Y = 0.00
	Z = 0.03
	wX = 0.00
	wY = 0.1
	wZ = 0.00
	Cmd = [ActualPosition[0]+X, ActualPosition[1]+Y, ActualPosition[2]+Z, ActualPosition[3]+wX, ActualPosition[4]+wY, ActualPosition[5]+wZ]
	motionProxy.gotoPosition("LLeg", Robot.motion.SPACE_SUPPORT_LEG, Cmd, Robot.motion.AXIS_MASK_ALL, InterpolationTimeForThisSection, Robot.motion.INTERPOLATION_SMOOTH)

	#####################################################################
	#####################################################################
	InterpolationTimeForThisSection = 0.4 #In seconds

	# Bend The Torso Backward
	Rx = 0.2
	Ry = 0.1
	Id1 = motionProxy.post.gotoTorsoOrientation(Rx,Ry,InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Move Head
	Id2 = motionProxy.post.gotoAngle('HeadPitch', -0.1, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Move Arms
	motionProxy.post.gotoAngle('LShoulderPitch', 100 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	motionProxy.post.gotoAngle('LElbowRoll', 0 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	motionProxy.post.gotoAngle('RShoulderPitch', 70 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	motionProxy.post.gotoAngle('RElbowRoll', 80 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Shoot The LEFT_LEG
	X = 0.10
	Y = 0.00
	Z = 0.05
	wX = 0.00
	wY = 0.00
	wZ = 0.00
	Cmd = [ActualPosition[0]+X, ActualPosition[1]+Y, ActualPosition[2]+Z, ActualPosition[3]+wX, ActualPosition[4]+wY, ActualPosition[5]+wZ]
	motionProxy.gotoPosition("LLeg", Robot.motion.SPACE_SUPPORT_LEG, Cmd, Robot.motion.AXIS_MASK_ALL, InterpolationTimeForThisSection, Robot.motion.INTERPOLATION_SMOOTH)

	#####################################################################
	#####################################################################
	InterpolationTimeForThisSection = 0.5 #In seconds

	# Straighten The Torso
	Rx = 0.2
	Ry = 0.0
	motionProxy.post.gotoTorsoOrientation(Rx,Ry,InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Move Head
	motionProxy.post.gotoAngle('HeadPitch', 0.0, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Move Arms
	Id3 = motionProxy.post.gotoAngle('LShoulderPitch', 120 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	Id4 = motionProxy.post.gotoAngle('LElbowRoll', -80 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	Id5 = motionProxy.post.gotoAngle('RShoulderPitch',120 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)
	Id6 = motionProxy.post.gotoAngle('RElbowRoll', 80 * Robot.motion.TO_RAD, InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Lower The LEFT_LEG
	X = 0.00
	Y = 0.00
	Z = 0.02
	wX = 0.00
	wY = 0.00
	wZ = 0.00
	Cmd = [ActualPosition[0]+X, ActualPosition[1]+Y, ActualPosition[2]+Z, ActualPosition[3]+wX, ActualPosition[4]+wY, ActualPosition[5]+wZ]
	motionProxy.gotoPosition("LLeg", Robot.motion.SPACE_SUPPORT_LEG, Cmd, Robot.motion.AXIS_MASK_ALL, InterpolationTimeForThisSection, Robot.motion.INTERPOLATION_SMOOTH)

	#####################################################################
	#####################################################################
	InterpolationTimeForThisSection = 0.5 #In seconds

	# Straighten The Torso
	Rx = 0.0
	Ry = 0.0
	motionProxy.post.gotoTorsoOrientation(Rx,Ry,InterpolationTimeForThisSection,Robot.motion.INTERPOLATION_SMOOTH)

	# Down The LEFT_LEG
	X = 0.00
	Y = 0.00
	Z = 0.00
	wX = 0.00
	wY = 0.00
	wZ = 0.00
	Cmd = [ActualPosition[0]+X, ActualPosition[1]+Y, ActualPosition[2]+Z, ActualPosition[3]+wX, ActualPosition[4]+wY, ActualPosition[5]+wZ]
	motionProxy.gotoPosition("LLeg", Robot.motion.SPACE_SUPPORT_LEG, Cmd, Robot.motion.AXIS_MASK_ALL, InterpolationTimeForThisSection, Robot.motion.INTERPOLATION_SMOOTH)

	#####################################################################
	#####################################################################
	# Go to Double Support Mode
	motionProxy.setSupportMode(Robot.motion.SUPPORT_MODE_DOUBLE_RIGHT)
	time.sleep(3)
	motionProxy.setBalanceMode(Robot.motion.BALANCE_MODE_OFF)

