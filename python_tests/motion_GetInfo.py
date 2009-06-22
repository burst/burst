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
print "Body has %s joints" % NumJoints

