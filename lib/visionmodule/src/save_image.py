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
  import motion

# Replace here with your robot's IP address
#IP = "192.168.7.108"
#PORT = 9559
IP = "127.0.0.1"
PORT = 9560

#IP_REMOTE = "127.0.0.1"
#PORT_REMOTE = 54010

# Create a proxy to Vision module
try:
  visionProxy = ALProxy("vision", IP, PORT)
except Exception, e:
  print "Error when creating vision proxy:"
  print str(e)
  exit(1)

visionProxy.registerToVIM()

#visionProxy.saveImageRemote("/var/tmp/")
visionProxy.saveImage("/var/tmp/")

visionProxy.unRegisterFromVIM()

print "Test terminated successfully"
