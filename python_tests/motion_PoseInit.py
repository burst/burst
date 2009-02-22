"""
PoseInit

Small example to make Nao go to its initial position.
"""

from motion_CurrentConfig import *


####
# Create python broker
try:
  broker = ALBroker("pythonBroker","127.0.0.1",9999,IP, PORT)
except RuntimeError,e:
  print("cannot connect")
  exit(1)

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
torsoAngle = 0.0 * motion.TO_RAD
wideAngle = 0 * motion.TO_RAD

#Get the Number of Joints
NumJoints = len(motionProxy.getBodyJointNames())

# Define The Initial Position
if (NumJoints == 22) :
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -90.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, 
    0.0, wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, -wideAngle, 
    0.0, -wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, wideAngle, 
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 80.0 * motion.TO_RAD]
elif (NumJoints == 26) :
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -90.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,0.0,
    0.0, wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, -wideAngle, 
    0.0, -wideAngle, -kneeAngle/2-torsoAngle, kneeAngle, -kneeAngle/2, wideAngle, 
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 0.0]
else :
  print "Unexpected number of joints"
  exit(1)

# Set balancer Off to Allow Full control of Nao joints
motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
# Send angles through a smooth interpolation of one seceond.
motionProxy.gotoBodyAnglesWithSpeed(InitialPosition ,30, motion.INTERPOLATION_SMOOTH)
