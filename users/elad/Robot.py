import os, sys, time
import Util
sys.path.append(os.path.join(os.path.dirname(sys.modules['Robot'].__file__), '../../lib'))
from burst import *
import burst
import motion

# The robot's IP and port.
ip = burst.ip#"192.168.7.158"
port = burst.port#9559

broker = None
proxies = []

def init():
	global broker
	if broker is None:
		broker = ALBroker("pythonBroker", "127.0.0.1", 9999, ip, port)

def getBroker():
	return broker

motionProxy = None

def getMotionProxy():
	global motionProxy
	global proxies
	if motionProxy is None:
		motionProxy = ALProxy("ALMotion")
		proxies.append(motionProxy)
	return motionProxy

speechProxy = None

def getSpeechProxy():
	global speechProxy
	global proxies
	if speechProxy is None:
		speechProxy = ALProxy("ALTextToSpeech")
		proxies.append(speechProxy)
	return speechProxy

def shutdown():
	pass

