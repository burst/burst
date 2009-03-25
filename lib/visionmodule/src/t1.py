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
IP = "192.168.7.159" 
PORT = 9559

# Create a proxy to ALMotion
try:
  motionProxy = ALProxy("ALMotion", IP, PORT)
except Exception, e:
  print "Error when creating motion proxy:"
  print str(e)
  exit(1)

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

newHeadYaw = 0.2

for i in range(0, 5):
  time.sleep(0.5)
  print(i)

  # head between -2 (right) to 2 (left)
  # ball between 0 (left) to 640 (right)

  newHeadYaw = 0.2
  motionProxy.gotoAngle("HeadYaw",newHeadYaw,TimeInterpolation*10,1)


#  if(val):
#    if(val[0]>0):
#      # we detected logos !
#      # for each logo, we can read its coordinates
#      print "Number of logos detected:", val[0]
#      for i in range(0, val[0]):
#        print "  ID: %d , x: %f, y: %f, sx: %f" % (val[i+1][0], val[i+1][1], val[i+1][2], val[i+1][3])
#  else:
#    print "* No logo detected"

motionProxy.setJointStiffness('HeadYaw',0.0,TimeInterpolation)

print "Test terminated successfully" 

