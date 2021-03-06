import os
import sys
import time

path = os.environ.get("AL_DIR")
home = os.environ.get("HOME")

# import NaoQi lib
if path == "None":
  print "the environnement variable AL_DIR is not set, aborting..."
  sys.exit(1)
else:
  alPath = path + "/extern/python/aldebaran"
  alPath = alPath.replace("~", home)
  alPath = alPath.replace("'", "")
  sys.path.append(alPath)
  import naoqi
  from naoqi import ALBroker
  from naoqi import ALModule
  from naoqi import ALProxy
  from naoqi import ALBehavior

# Replace here with your robot's IP address
IP = "192.168.7.158"
PORT = 9559

#IP_REMOTE = "127.0.0.1"
#PORT_REMOTE = 54010

# Create a proxy to ALMotion
try:
  motionProxy = ALProxy("ALMotion", IP, PORT)
except Exception, e:
  print "Error when creating motion proxy:"
  print str(e)
  exit(1)

# Create a proxy to Vision module
try:
  visionProxy = ALProxy("vision", IP, PORT)
except Exception, e:
  print "Error when creating vision proxy:"
  print str(e)
  exit(1)

visionProxy.registerToVIM()

# ALMemory variable where the ALVisionLogo modules
# outputs its results
memValue = "/BURST/Vision/BallX"

# Create a proxy to ALMemory
try:
  memoryProxy = ALProxy("ALMemory", IP, PORT)
except Exception, e:
  print "Error when creating memory proxy:"
  print str(e)
  exit(1)

# A simple loop that reads the memValue and checks
# whether logos are detected
#
# Note : using C++, you can instead use a callback
# to get notified when the memValue changes

TimeInterpolation = 0.05
motionProxy.setJointStiffness('HeadYaw',1.0,TimeInterpolation)
visionProxy.getBall()
time.sleep(1.0)

