"""
ArmsMotionBalancing

Small example to make Nao move his arms

"""
from motion_CurrentConfig import *


#####
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

#Get the Number of Joints
NumJoints = len(motionProxy.getBodyJointNames())

# ============================
# Defines The Start Position
if (NumJoints == 22) :
  poseStart = [0.0,0.0,
    90.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, -90.0 * motion.TO_RAD,  -90.0 * motion.TO_RAD,
    0.0, 0.0, -20.0 * motion.TO_RAD, 40.0 * motion.TO_RAD, -20.0 * motion.TO_RAD, 0.0, 
    0.0, 0.0, -20.0 * motion.TO_RAD, 40.0 * motion.TO_RAD, -20.0 * motion.TO_RAD, 0.0, 
    90.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 90.0 * motion.TO_RAD]
elif (NumJoints == 26) :
  poseStart = [0.0,0.0,
    90.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, -90.0 * motion.TO_RAD,  -90.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 0.0,
    0.0, 0.0, -20.0 * motion.TO_RAD, 40.0 * motion.TO_RAD, -20.0 * motion.TO_RAD, 0.0, 
    0.0, 0.0, -20.0 * motion.TO_RAD, 40.0 * motion.TO_RAD, -20.0 * motion.TO_RAD, 0.0, 
    90.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 0.0]
else :
  print "Unexpected number of joints"
  exit(1)

motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
# Send angles throw a Smooth interpolation of 1s
motionProxy.gotoBodyAngles( poseStart ,1.0, motion.INTERPOLATION_SMOOTH)

#*************************************************************
# If You UnComment these three lines the robot will automatically compensate arm motions
#*************************************************************
# motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_RIGHT)
# motionProxy.setBalanceMode(motion.BALANCE_MODE_AUTO)
# time.sleep(1)

# Some Define
tInterpolation = 0.5

if (NumJoints == 22) :
  angleL = [0.0, 0.0 * motion.TO_RAD,-90.0 * motion.TO_RAD, 0.0]
  angleR = [0.0, 0.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 0.0]
elif (NumJoints == 26) :
  angleL = [0.0, 0.0 * motion.TO_RAD,-90.0 * motion.TO_RAD, 0.0,0.0,0.0]
  angleR = [0.0, 0.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 0.0,0.0,0.0]
else :
  print "Unexpected number of Joint"
  exit(1)

#*************************************************************
#  ------------------- ARM MOTION --------------------------
#*************************************************************
for i in range(0,5):
  motionProxy.post.gotoChainAngles("RArm", angleR, tInterpolation, motion.INTERPOLATION_SMOOTH)
  motionProxy.post.gotoAngle("LShoulderRoll", 90 * motion.TO_RAD, tInterpolation, motion.INTERPOLATION_SMOOTH)
  motionProxy.post.gotoAngle("LShoulderPitch",90 * motion.TO_RAD, tInterpolation, motion.INTERPOLATION_SMOOTH)
  motionProxy.post.gotoAngle("LElbowYaw",    -90 * motion.TO_RAD, tInterpolation, motion.INTERPOLATION_SMOOTH)
  motionProxy.gotoAngle("LElbowRoll",   -90 * motion.TO_RAD, tInterpolation, motion.INTERPOLATION_SMOOTH)

  motionProxy.post.gotoChainAngles("LArm", angleL, tInterpolation,motion.INTERPOLATION_SMOOTH)  
  motionProxy.post.gotoAngle("RShoulderRoll",-90*motion.TO_RAD,tInterpolation,motion.INTERPOLATION_SMOOTH)
  motionProxy.post.gotoAngle("RShoulderPitch",90*motion.TO_RAD,tInterpolation,motion.INTERPOLATION_SMOOTH)
  motionProxy.post.gotoAngle("RElbowYaw",90*motion.TO_RAD,tInterpolation,motion.INTERPOLATION_SMOOTH)
  motionProxy.gotoAngle("RElbowRoll",90*motion.TO_RAD,tInterpolation,motion.INTERPOLATION_SMOOTH)
  
# Go to Start position
motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
motionProxy.gotoBodyAnglesWithSpeed(poseStart, 50, motion.INTERPOLATION_SMOOTH)
