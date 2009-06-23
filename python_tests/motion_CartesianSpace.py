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

# Get The Initial Position of the Right Arm [x, y, z, wx, wy, wz]
# in the Support Leg Space
InitialPosition = motionProxy.getPosition('RArm', motion.SPACE_SUPPORT_LEG)
print InitialPosition

# Initialize Target Position to Initial Position
TargetPosition = InitialPosition

# Create a Target Position of +8cm along X axis (first coordinate)
TargetPosition[0] += 0.04

# Move the Right Arm with to the Target Position relative to
#   Support Leg Space in 2.0s with Smooth Interpolation.
# A Velocity Mask is used so orientations of the End effector are
#   not controlled.
motionProxy.gotoPosition('RArm', motion.SPACE_SUPPORT_LEG, TargetPosition, motion.AXIS_MASK_VEL, 2.0, motion.INTERPOLATION_SMOOTH)

# Create a Target Position of -8cm along Y axis (second coordinate)
TargetPosition[1] += -0.08
motionProxy.gotoPosition('RArm', motion.SPACE_SUPPORT_LEG, TargetPosition, motion.AXIS_MASK_VEL, 2.0, motion.INTERPOLATION_SMOOTH)

TargetPosition[0] += -0.08
motionProxy.gotoPosition('RArm', motion.SPACE_SUPPORT_LEG, TargetPosition, motion.AXIS_MASK_VEL, 2.0, motion.INTERPOLATION_SMOOTH)

TargetPosition[1] += 0.08
motionProxy.gotoPosition('RArm', motion.SPACE_SUPPORT_LEG, TargetPosition, motion.AXIS_MASK_VEL, 2.0, motion.INTERPOLATION_SMOOTH)