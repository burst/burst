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


IP = "127.0.0.1"  # Put here the IP address of your robot
#~ IP = "10.0.252.170"  # Put here the IP address of your robot

PORT = 54010

####
# Creat proxy on vision module

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
####
# Save image in remote mode
print "1"
#sampleProxy.saveImageRemote("/var/tmp/myBeautifullPictureRemote") #/var/volatile/log/myBeautifullPictureRemote
print "2"
time.sleep(1)
print "3"
#sampleProxy.saveImage("/var/tmp/myBeautifullPictureLocal") #/var/volatile/log/myBeautifullPictureLocal

ccc = sampleProxy.getBallAreaRemote()
print ccc

time.sleep(2)
print "4"
sampleProxy.unRegisterFromVIM()
print "5"

print "end of test vision python script"

