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
IP = "192.168.7.108"
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

TimeInterpolation = 0.05
motionProxy.setJointStiffness('HeadYaw',1.0,TimeInterpolation)
motionProxy.gotoAngle("HeadYaw",0.31,TimeInterpolation*10,1) #0.23
visionProxy.getBall()
time.sleep(1.0)

#motionProxy.gotoAngle("HeadYaw",-0.15,TimeInterpolation*10,1) #0.23
#print (10*motion.TO_RAD)
#exit(0)

while True:
#for i in range(0, 1):
  #time.sleep(0.1)
  #print(i)

  #visionProxy.getBallRemote()
  visionProxy.getBall()
  visionProxy.getBall()

  val = memoryProxy.getData(memValue, 0)
  #val = 320

  # head between -2 (right) to 2 (left)
  # ball between 0 (left) to 640/320 (right)
  # camera is 46.4 horizontal, 34.8 vertical (specs), fov 58 (specs)

  if(val):
    if(val>0):
      print "Ball X: ", val
      currentHeadYaw = motionProxy.getAngle("HeadYaw")
      print "currentHeadYaw: %f" % currentHeadYaw
      xtodeg = ((160.0-val)/160.0) # between 1 (left) to -1 (right)
      print "xtodeg: %f" % xtodeg
      
      if (abs(xtodeg)>0.05):
       xtodegfactor = 23.2 #46.4/2
       newHeadYaw = currentHeadYaw + (xtodeg*xtodegfactor*motion.TO_RAD)
       print "newHeadYaw: %f" % newHeadYaw
       #motionProxy.setAngle("HeadYaw",(320.0-val)/320.0/2)
       motionProxy.gotoAngle("HeadYaw",newHeadYaw,TimeInterpolation*10,1)
       #print "test: %f" % ((320.0-val)/320.0/2)
  else:
    print "* No ball detected"


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
visionProxy.unRegisterFromVIM()

print "Test terminated successfully" 
