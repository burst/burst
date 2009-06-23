#!/usr/bin/python

##############################################################################
# Name: subscribe_tester.py
#
# Summary: Show how to create a module and use the callback mechanism.
#
# Usage: subscribe_tester.py [Naoqi IP address, local IP address]
#        - Naoqi IP: address Naoqi is listening to.
#        - local IP: address where you launch the script and that Naoqi can
#          use to call you back.
#
# Description:
#   - Create a Python broker using the provided Naoqi and local addresses.
#   - Create an ALModule object (markHandler) with its call back function.
#   - Call ALMemory's subscribeOnDataChange so that markHandler.onMarkChange()
#     is called whenever the detection results change.
#   - Wait for some time.
#   - Check that we got called.
#
##############################################################################

# Used in debug logs.
testName = "python: vision_onMarkDataChange: "

import os
import sys
import time

# IP and PORT default values.
LOCAL_IP = "127.0.0.1"
LOCAL_PORT = 9999
IP = "127.0.0.1"
PORT = 9560

# Read IP address from first argument if any.
if len( sys.argv ) > 1:
  IP = sys.argv[1]

if len( sys.argv ) > 2:
  LOCAL_IP = sys.argv[2]

path = `os.environ.get("AL_DIR")`
home = `os.environ.get("HOME")`

########################################################
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
  from vision_definitions import*

##############################################################################
# Definition of our python module.
# The main point here is to declare a call back function "onMarkChange"
# which will be called by ALMemory whenever the variable changes.
class MarkHandlerModule(ALModule):
  def __init__(self, name):
    ALModule.__init__(self, name)
    self.BIND_PYTHON(name, "onMarkChange")
    self.mHasDetectedMarks = False

  # Call back function registered with subscribeOnDataChange that handles
  # changes in LandMarkDetection results.
  def onMarkChange(self, dataName, value, msg):
    print str(value)
    if (len(value) != 0):
      self.mHasDetectedMarks = True

  def hasDetectedMarks(self):
    return self.mHasDetectedMarks

##############################################################################


testFailed = 0

# ALMemory variable where the ALLandMarkdetection module outputs its results.
memValue = "/Test"

# Create a python broker on the local machine.
broker = ALBroker("pythonBroker", LOCAL_IP, LOCAL_PORT, IP, PORT)

import pdb; pdb.set_trace()

try:
  markHandlerName = "markHandler"
  # Create our module object.
  markHandler = MarkHandlerModule(markHandlerName)

  # Have module.onMarkChange called back when detection results change.
  memoryProxy = ALProxy("ALMemory")
  memoryProxy.subscribeOnData(memValue, markHandler.getName(), "",
    "onMarkChange")

  # Let the NaoMark detection run for a little while.
  time.sleep(5)

  # Shut the Python Broker down
  broker.shutdown()

except Exception, e:
  print "%s Error:"  %(testName)
  print str(e)
  testFailed = 1

import pdb; pdb.set_trace()

# Check that we detected some Naomarks.
if (markHandler.hasDetectedMarks() == False):
  print "%s : Could not detect Naomarks !" % (testName)
  testFailed = 1

if (testFailed == 1):
  print "%s : Failed" % (testName)
  exit(1)

print "%s : Success" % (testName)

