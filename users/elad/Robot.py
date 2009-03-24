import os, sys, time
import Util
sys.path.append(os.path.join(os.path.dirname(sys.modules['Robot'].__file__), '../../lib'))
from burst import *
import burst
import motion

# The robot's IP and port.
ip = burst.ip#"192.168.7.108"#burst.ip
port = burst.port#9559#burst.port

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
#		print "Creating a proxy. This is a debugging message, in case multiple proxies cause some tasks not to be killed by the killAll method."
	return motionProxy

speechProxy = None

def getSpeechProxy():
	global speechProxy
	global proxies
	if speechProxy is None:
		speechProxy = ALProxy("ALTextToSpeech")
		proxies.append(speechProxy)
#		print "Creating a proxy. This is a debugging message, in case multiple proxies cause some tasks not to be killed by the killAll method."
	return speechProxy

def shutdown():
	pass
#	global proxies
#	global broker
#	for proxy in proxies:
#		proxy.__del__()
#	broker.__del__()
#	print "done?"




