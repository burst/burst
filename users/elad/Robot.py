import os, sys, time
import Util

sys.path.append('../../lib')
from burst import *
import burst
import motion

# The robot's IP and port.
ip = "192.168.7.106" #burst.ip
port = 9559 #burst.port
broker = None

def init():
#	if Util.runningOnRobot():
#		broker = ALBroker("pythonBroker", "127.0.0.1", 9999, "127.0.0.1", port)	
#	else:
		broker = ALBroker("pythonBroker", "127.0.0.1", 9999, ip, port)

def getBroker():
	return broker

motionProxy = None

def getMotionProxy():
	global motionProxy
	if motionProxy == None:
		motionProxy = ALProxy("ALMotion")
	return motionProxy

speechProxy = None

def getSpeechProxy():
	global speechProxy
	if speechProxy == None:
		speechProxy = ALProxy("ALTextToSpeech")
	return speechProxy
	
