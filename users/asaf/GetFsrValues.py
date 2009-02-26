import os
import sys
import time

path = `os.environ.get("AL_DIR")`
home = `os.environ.get("HOME")` 

IP = "10.0.252.190" # Robot IP  Address
PORT = 9559

# ====================
# import naoqi lib
if path == "None":
  print "the environnement variable AL_DIR is not set, aborting..."
  sys.exit(1)
else:
  alPath = path + "/extern/python/aldebaran"
  alPath = alPath.replace("~", home)
  alPath = alPath.replace("'", "")
  sys.path.append(alPath)
  import naoqi
  from naoqi import ALProxy


# ====================
# Create proxy to ALMemory
memoryProxy = ALProxy("ALMemory",IP,PORT)

# Get The Left Foot Force Sensor Values
LFsrFL = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value",0)
LFsrFR = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/Value",0)
LFsrBL = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/Value",0)
LFsrBR = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/Value",0)

print( "Left FSR : %.2f %.2f %.2f %.2f" %  (LFsrFL, LFsrFR, LFsrBL, LFsrBR) )

# Get The Right Foot Force Sensor Values
RFsrFL = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/Value",0)
RFsrFR = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/FrontRight/Sensor/Value",0)
RFsrBL = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/RearLeft/Sensor/Value",0)
RFsrBR = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/RearRight/Sensor/Value",0)

print( "Right FSR : %.2f %.2f %.2f %.2f" %  (RFsrFL, RFsrFR, RFsrBL, RFsrBR) )