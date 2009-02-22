# This test demonstrates how to use the ALVisionLogo module.
# Note that you might not have this module depending on your distribution
#
# - We first instantiate a proxy to the ALVisionLogo module 
#     Note that this module should be loaded on the robot's naoqi.
#     The module output its results in ALMemory in a variable
#     called "extractors/alvisionlogo/logopositions"

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

# Create a proxy to ALVisionLogo
try:
  logoProxy = ALProxy("ALVisionLogo", IP, PORT)
except Exception, e:
  print "Error when creating logo detection proxy:"
  print str(e)
  exit(1)

# ALMemory variable where the ALVisionLogo modules
# outputs its results
memValue = "extractors/alvisionlogo/logopositions"

# Subscribe to the ALVisionLogo proxy
# This means that the module will write in memValue with
# the given period below
period = 500
logoProxy.subscribe("Test_Logo", [ period ] )


# Create a proxy to ALMemory
try:
  memoryProxy = ALProxy("ALMemory", IP, PORT)
except Exception, e:
  print "Error when creating memory proxy:"
  print str(e)
  exit(1)

print "Creating landmark detection proxy"

# A simple loop that reads the memValue and checks
# whether logos are detected
#
# Note : using C++, you can instead use a callback
# to get notified when the memValue changes

for i in range(0, 20):
  time.sleep(0.5)
  print(i)
  val = memoryProxy.getData(memValue, 0)

  if(val):
    if(val[0]>0):
      # we detected logos !
      # for each logo, we can read its coordinates
      print "Number of logos detected:", val[0]
      for i in range(0, val[0]):
        print "  ID: %d , x: %f, y: %f, sx: %f" % (val[i+1][0], val[i+1][1], val[i+1][2], val[i+1][3])
  else:
    print "* No logo detected"

# Unsubscribe the module
logoProxy.unsubscribe("Test_Logo")

print "Test terminated successfully" 

