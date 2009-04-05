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


#IP = "127.0.0.1"  # Put here the IP address of your robot
IP = "192.168.7.108"

#PORT = 54010
PORT = 9559

####
# Creat proxy on vision module

# Create a proxy to ALMotion
try:
  motionProxy = ALProxy("ALMotion", IP, PORT)
except Exception, e:
  print "Error when creating motion proxy:"
  print str(e)
  exit(1)

#________________________________
# Generic Proxy creation 
#________________________________

try:
  visionProxy = ALProxy("vision",IP,PORT)
except Exception,e:
  print "Error when creating visionProxy:"
  print str(e)
  exit(1)
#________________________________
# Remote procedure call
#________________________________

motionProxy.setBodyStiffness(1.0,0.05)

#try:
#  visionProxy.start(1)
#  time.sleep(10)
#  visionProxy.stop()
#except Exception,e:
#  print "visionProxy test Failed"
#  exit(1)
#
#motionProxy.setBodyStiffness(0.0,0.05)
#
#exit(0)

print "Creating vision proxy"

try:
  sampleProxy = ALProxy("vision", IP, PORT)
except Exception,e:
  print "Error when creating vision proxy:"
  print str(e)
  exit(1)

time.sleep(1)

print "Registering to VIM"
sampleProxy.registerToVIM()

print "done"

#time.sleep(3)

####
# Save image in remote mode
print "1"
#sampleProxy.saveImage("/tmp/") #saveImageRemote
#print "2"
#time.sleep(3)

#a = sampleProxy.getBallRemote() #getBallRemote
a = sampleProxy.getBall() #getBallRemote

print a

#print "2"
#sampleProxy.saveImage("/var/tmp/myBeautifullPictureLocal") #/var/volatile/log/myBeautifullPictureLocal

#time.sleep(1)
#print "3"
#sampleProxy.unRegisterFromVIM()
#print "4"

memoryProxy = ALProxy("ALMemory", IP, PORT)
memoryProxy.getData("/BURST/Vision/BallX", -1)
memoryProxy.getData("/BURST/Vision/BallY", -1)
memoryProxy.getData("/BURST/Vision/BallWidth", -1)
memoryProxy.getData("/BURST/Vision/BallHeight", -1)

print "end of gvm_useGVMsample python script"
