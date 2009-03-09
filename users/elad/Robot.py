import os, sys, time
import Util

sys.path.append('../../lib')
from burst import *
import burst
import motion

# Define the variables for the robot's IP and port.
ip = "192.168.7.666" # The default IP.
port = 9559 # The default port.
broker = None

def init():
#	if Util.runningOnRobot():
#		broker = ALBroker("pythonBroker", "127.0.0.1", 9999, "127.0.0.1", port)	
#	else:
		broker = ALBroker("pythonBroker", "127.0.0.1", 9999, ip, port)

def getBroker():
	return broker
	
def getMotionProxy():
	return ALProxy("ALMotion")

def getSpeechProxy():
	return ALProxy("ALTextToSpeech")
	
