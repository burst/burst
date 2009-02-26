"""
Torso orientation

Small example to make NaoQi move its torso

"""
from motion_CurrentConfig import *


#####
# Create python broker


try:
        broker = ALBroker("pythonBroker","127.0.0.1",9999,IP, PORT)
except RuntimeError,e:
        print("cannot connect")
        exit(1)


# let time to create broker thread execution
time.sleep(3)


####
# Create motion proxy
print "Creating motion proxy"


try:
  motionProxy = ALProxy("ALMotion")
except Exception,e:
  print "Error when creating motion proxy:"
  print str(e)
  exit(1)



kneeAngle = 60.0 * motion.TO_RAD

#Get the Number of Joints
NumJoints = len(motionProxy.getBodyJointNames())

# Define The Initial Position
if (NumJoints == 22) :
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, 
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2, 0.0 * motion.TO_RAD, 
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2,0.0 * motion.TO_RAD, 
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 80.0 * motion.TO_RAD]
elif (NumJoints == 26) :
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,0.0,
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2, 0.0 * motion.TO_RAD, 
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2, -0.0 * motion.TO_RAD, 
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 0.0]
else :
  print "Unexpected number of joints"
  exit(1)


motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
# Send angles through a smooth interpolation of one second
motionProxy.gotoBodyAngles( InitialPosition ,1.0, motion.INTERPOLATION_SMOOTH)


# Create two floats to control torso orientation
# Be aware that a too much value will create a Excessive joint Command due to singularity !
wx = 0.2
wy = 0.0

motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
time.sleep(1)
motionProxy.setBalanceMode(motion.BALANCE_MODE_AUTO)

time.sleep(2)

# Move Torso orientation to wx and wy in the Support Leg Space
# in 2s with smooth interpolation
motionProxy.gotoTorsoOrientation(wx,wy,2.0,motion.INTERPOLATION_SMOOTH)

# Stay in position during 2s
time.sleep(2)

wx = 0.0
wy = 0.5
motionProxy.gotoTorsoOrientation(wx,wy,2.0,motion.INTERPOLATION_SMOOTH)

# Stay in position during 2s
time.sleep(2)

wx = 0.0
wy = 0.0
motionProxy.gotoTorsoOrientation(wx,wy,2.0,motion.INTERPOLATION_SMOOTH)


# Don't forgot to call this, otherwise strange behaviour may occur
motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
