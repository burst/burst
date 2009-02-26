import os
import sys
import time

path = `os.environ.get("AL_DIR")`
home = `os.environ.get("HOME")` 

IP = "192.168.2.107" # Robot IP  Address
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

from time import sleep

def printvalues():
    # Get the Gyrometers Values
    GyrX = memoryProxy.getData("Device/SubDeviceList/InertialSensor/GyrX/Sensor/Value",0)
    GyrY = memoryProxy.getData("Device/SubDeviceList/InertialSensor/GyrY/Sensor/Value",0)
    print ("Gyrometers value X: %.3f, Y: %.3f" % (GyrX, GyrY))

    # Get the Accelerometers Values
    AccX = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AccX/Sensor/Value",0)
    AccY = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AccY/Sensor/Value",0)
    AccZ = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AccZ/Sensor/Value",0)
    print ("Accelerometers value X: %.3f, Y: %.3f, Z: %.3f" % (AccX, AccY,AccZ))

    # Get the Compute Torso Angle in radian
    TorsoAngleX = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",0)
    TorsoAngleY = memoryProxy.getData("Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",0)
    print ("Torso Angles [radian] X: %.3f, Y: %.3f" % (TorsoAngleX, TorsoAngleY))

while True:
    printvalues()
    sleep(0.1)

