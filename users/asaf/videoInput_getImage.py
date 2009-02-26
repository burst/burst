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


IP = "10.0.252.149"  # Put here the IP address of your robot
#~ IP = "10.0.252.170"  # Put here the IP address of your robot

PORT = 9559

####
# Create proxy on NaoCam

print "Creating NaoCam proxy"

try:
  camProxy = ALProxy("NaoCam", IP, PORT)
except Exception,e:
  print "Error when creating vision proxy:"
  print str(e)
  exit(1)

####
# Register a Generic Video Module

resolution = 1       #kQVGA
colorSpace = 9 # kYUVColorSpace
fps = 30

nameId = camProxy.register("python_GVM", resolution, colorSpace, fps)
print nameId

print 'getting direct raw images in local'
for i in range(0, 50):
  camProxy.getDirectRawImageLocal(nameId)
  camProxy.releaseDirectRawImage(nameId)

print 'getting direct raw images in remote'
for i in range(0, 50):
  camProxy.getDirectRawImageRemote(nameId)

resolution = 2       #kVGA
camProxy.setResolution(nameId, resolution)

print 'getting images in local'
for i in range(0, 50):
  camProxy.getImageLocal(nameId)
  camProxy.releaseImage(nameId)

print 'getting images in remote'
for i in range(0, 50):
  camProxy.getImageRemote(nameId)


camProxy.unRegister(nameId)


print 'end of gvm_getImageLocal python script'

