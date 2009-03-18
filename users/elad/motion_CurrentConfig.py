"""
 This file will be read by all other scripts in this directory.

 Use it to put the IP and port of your robot once for all.
"""
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
  from naoqi import *
  import motion


IP = "192.168.7.106" # Put here the IP address of your robot
PORT = 9559


if (IP == ""):
  print "IP address not defined, aborting"
  print "Please define it in " + __name__  
  exit(1)

# ======================= PRINT  ==========================
print "CurrentConfig: Using IP: " + str(IP) + " and port: "  + str(PORT)

