import os
import sys
import time

path = `os.environ.get("AL_DIR")`
home = `os.environ.get("HOME")`
IP = "192.168.7.110" # Robot IP  Address
PORT=9559

# import naoqi lib
if path == "None":
  print "the environment variable AL_DIR is not set, aborting..."
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

# create proxy
try:
  alsonarProxy = ALProxy("ALSonar",IP,PORT)
except RuntimeError,e:
  print "error while creation alsonar's proxy"
  exit(1)

# subscribe to ALUltraound
try:
  period = 2000 # minimum should be 240ms according to documentation
  alsonarProxy.subscribe("test", [ period ] )
  print "subscription to ALSonar is ok"
except RuntimeError,e:
  print "error while subscribing to alsonar"
  exit(1)


# processing
# ....
print "processing"

# ====================
# Create proxy to ALMemory
memoryProxy = ALProxy("ALMemory",IP,PORT)

# Get The Left Foot Force Sensor Values

for i in xrange(1,2000):
    US = memoryProxy.getData("extractors/alsonar/distances",0)
    print US

#~ # unsubscribe to ALUltraound
#~ try:
  #~ alsonarProxy.unsubscribe("test")
  #~ print "unsubscription to ALSonar is ok"
#~ except RuntimeError,e:
  #~ print "error while unsubscribing to alsonar"
  #~ exit(1)

#~ print "quitting"
#~ exit(0)
