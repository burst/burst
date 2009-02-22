# This test demonstrates how to use the ALLandMarkDetection module.
# Note that you might not have this module depending on your distribution
#
# - We first instantiate a proxy to the ALLandMarkDetection module 
#     Note that this module should be loaded on the robot's naoqi.
#     The module output its results in ALMemory in a variable
#     called "extractors/allandmarkdetection/landmarkdetected"

# - We then read this AlMemory value and check whether we get
#   interesting things.

import os
import sys
import time
path = `os.environ.get("AL_DIR")`
home = `os.environ.get("HOME")`

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
IP = "10.0.252.175" 

PORT = 9559

# Create a proxy to ALLandMarkDetection
try:
  landMarkProxy = ALProxy("ALLandMarkDetection", IP, PORT)
except Exception, e:
  print "Error when creating landmark detection proxy:"
  print str(e)
  exit(1)

# ALMemory variable where the ALLandMarkdetection modules
# outputs its results
memValue = "extractors/allandmarkdetection/landmarkdetected"

# Subscribe to the ALLandMarkDetection proxy
# This means that the module will write in memValue with
# the given period below
period = 500
landMarkProxy.subscribe("Test_LandMark", [ period ] )


# Create a proxy to ALMemory
try:
  memoryProxy = ALProxy("ALMemory", IP, PORT)
except Exception, e:
  print "Error when creating memory proxy:"
  print str(e)
  exit(1)

print "Creating landmark detection proxy"

# A simple loop that reads the memValue and checks
# whether landmarks are detected
#
# Note : using C++, you can instead use a callback
# to get notified when the memValue changes

for i in range(0, 20):
  time.sleep(0.5)
  val = memoryProxy.getData(memValue, 0)

  if(val):
    # check whether we got a list of values
    if(isinstance(val[0], list)):
       
      # we detected naomarks !
      # for each mark, we can read its ID and coordinates
      print "Number of Naomarks detected:", len(val)
      for i in range(0, len(val)):
	      print "  ID: %d , x: %f, y: %f, radius: %f" % (val[i][0], val[i][1], val[i][2], val[i][3])
  else:
    print "* No naomark detected"

# Unsubscribe the module
landMarkProxy.unsubscribe("Test_LandMark")

print "Test terminated successfully" 

