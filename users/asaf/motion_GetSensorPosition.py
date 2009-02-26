"""
GetSensorPosition

Small example to show use of getSensorPosition

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

print "Top camera initial position:"
print motionProxy.getSensorPosition("CameraTop", motion.SPACE_BODY)
print "Bottom camera initial position :"
print motionProxy.getSensorPosition("CameraBottom", motion.SPACE_BODY)

motionProxy.gotoAngleWithSpeed("HeadPitch" ,-40.0*motion.TO_RAD,10, motion.INTERPOLATION_SMOOTH)

print "Top camera final position:"
print motionProxy.getSensorPosition("CameraTop", motion.SPACE_BODY)
print "Bottom camera final position :"
print motionProxy.getSensorPosition("CameraBottom", motion.SPACE_BODY)

