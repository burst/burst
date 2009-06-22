import os
import sys
import time
from time import sleep
path = `os.environ.get("AL_DIR")`
home = `os.environ.get("HOME")`

IP = "192.168.2.107" # Robot IP  Address
PORT = 9559

# ====================
# import naoqi lib
if path == "None":
  print "the environnement variable AL_DIR is not set, aborting..."
  sys.exit(1)
else:
  alPath = path + "/extern/python/aldebaran"
  alPath = alPath.replace("~", home)
  alPath = alPath.replace("'", "")
  print "adding " + alPath
  sys.path.append(alPath)
  import naoqi
  from naoqi import ALProxy

# ====================
# Create proxy to ALMemory
memoryProxy = ALProxy("ALMemory",IP,PORT)



# Define The Initial Position ????
kneeAngle = 60.0 * motion.TO_RAD
torsoAngle = 0.0 * motion.TO_RAD
wideAngle = -3.0 * motion.TO_RAD

#Get the Number of Joints
NumJoints = len(motionProxy.getBodyJointNames())

# Define The Initial Position
if (NumJoints == 22) : #no hands
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, # missing hands?
    0.0, wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, -wideAngle,
    0.0, -wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, wideAngle,
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 80.0 * motion.TO_RAD] # missing hands?
elif (NumJoints == 26) :
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,0.0,
    0.0, wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, -wideAngle,
    0.0, -wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, wideAngle,
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 0.0]
else :
  print "Unexpected number of Joint"
  exit(1)








# Set balancer Off to allow full control of Nao joints
motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
# ??? The robot is leaning on right side. is this it?
motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_RIGHT)
# Send angles through a smooth interpolation (max motors speed: 30%)
motionProxy.gotoBodyAnglesWithSpeed(InitialPosition ,30, motion.INTERPOLATION_SMOOTH)
# Set the Balancer in Automatique Mode
motionProxy.setBalanceMode(motion.BALANCE_MODE_AUTO)
# Go to Simple Support RIGHT
motionProxy.setSupportMode(motion.SUPPORT_MODE_RIGHT)
time.sleep(3)
# Go to Double Support Mode
motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_RIGHT)
time.sleep(3)
motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)





# Bend The Torso Forward (Rx, Ry, Interpolation, ...)
motionProxy.post.gotoTorsoOrientation(0.2,0.0,0.4,motion.INTERPOLATION_SMOOTH)
# Bend The Torso Forward
motionProxy.post.gotoTorsoOrientation(0.2,0.4,0.4,motion.INTERPOLATION_SMOOTH)
# Bend The Torso Backward
Id1 = motionProxy.post.gotoTorsoOrientation(0.2,0.1,0.4,motion.INTERPOLATION_SMOOTH)
# Straighten The Torso (interpolation 0.5 - why?)
motionProxy.post.gotoTorsoOrientation(0.0,0.0,0.5,motion.INTERPOLATION_SMOOTH)


# Move Head (0.4seconds interpolation)
motionProxy.post.gotoAngle('HeadPitch', -0.4, 0.4,motion.INTERPOLATION_SMOOTH)
# Move Arms
Id3 = motionProxy.post.gotoAngle('LShoulderPitch', 70 * motion.TO_RAD, 0.4,motion.INTERPOLATION_SMOOTH)
Id4 = motionProxy.post.gotoAngle('LElbowRoll', -80 * motion.TO_RAD, 0.4,motion.INTERPOLATION_SMOOTH)
Id5 = motionProxy.post.gotoAngle('RShoulderPitch', 120 * motion.TO_RAD, 0.4,motion.INTERPOLATION_SMOOTH)
Id6 = motionProxy.post.gotoAngle('RElbowRoll', 0 * motion.TO_RAD, 0.4,motion.INTERPOLATION_SMOOTH)

# Raise The LEFT_LEG
ActualPosition = motionProxy.getPosition("LLeg", motion.SPACE_SUPPORT_LEG)
Cmd = [ActualPosition[0]-0.01, ActualPosition[1]+0.00, ActualPosition[2]+0.03, ActualPosition[3]+0.00, ActualPosition[4]+0.00, ActualPosition[5]+0.00]
motionProxy.gotoPosition("LLeg", motion.SPACE_SUPPORT_LEG, Cmd, motion.AXIS_MASK_ALL, 0.4, motion.INTERPOLATION_SMOOTH)
# Lower The LEFT_LEG
Cmd = [ActualPosition[0]+0.00, ActualPosition[1]+0.00, ActualPosition[2]+0.02, ActualPosition[3]+0.00, ActualPosition[4]+0.00, ActualPosition[5]+0.00]
motionProxy.gotoPosition("LLeg", motion.SPACE_SUPPORT_LEG, Cmd, motion.AXIS_MASK_ALL, 0.4, motion.INTERPOLATION_SMOOTH)
# Down The LEFT_LEG (interpolation 0.5)
Cmd = [ActualPosition[0]+0.00, ActualPosition[1]+0.00, ActualPosition[2]+0.00, ActualPosition[3]+0.00, ActualPosition[4]+0.00, ActualPosition[5]+0.00]
motionProxy.gotoPosition("LLeg", motion.SPACE_SUPPORT_LEG, Cmd, motion.AXIS_MASK_ALL, 0.5, motion.INTERPOLATION_SMOOTH)


# Get the Gyrometers Values
  GyrX = memoryProxy.getData("Device/SubDeviceList/InertialSensor/GyrX/Sensor/Value",0)
  GyrY = memoryProxy.getData("Device/SubDeviceList/InertialSensor/GyrY/Sensor/Value",0)
  print ("Gyrometers value X: %.3f, Y: %.3f" % (GyrX, GyrY))

# Get the Accelerometers Values
  AccX = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AccX/Sensor/Value",0)
  AccY = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AccY/Sensor/Value",0)
  AccZ = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AccZ/Sensor/Value",0)
  print ("Accelerometers value X: %.3f, Y: %.3f, Z: %.3f" % (AccX, AccY,AccZ))

# Get the Compute Torso Angle in radian
  TorsoAngleX = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",0)
  TorsoAngleY = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",0)
  print ("Torso Angles [radian] X: %.3f, Y: %.3f" % (TorsoAngleX, TorsoAngleY))
