"""
PoseZero

Set all the motors of the body to zero. Used for calibration

"""

from motion_CurrentConfig import *

####
# Create motion proxy

print "Creating motion proxy"


try:
  motionProxy = ALProxy("ALMotion",IP, PORT)
except Exception,e:
  print "Error when creating motion proxy:"
  print str(e)
  exit(1)


#Get the Number of Joints
NumJoints = len(motionProxy.getBodyJointNames())

ZeroPosition = [0.0] * NumJoints

# Set balancer Off to Allow Full control of Nao Joint
motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
# Send angles through a smooth interpolation (max speed of motors: 30%)
motionProxy.gotoBodyAnglesWithSpeed(ZeroPosition , 30, motion.INTERPOLATION_SMOOTH)
