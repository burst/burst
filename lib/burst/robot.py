import os, sys, time
import motion

from naoqi import ALBroker, ALProxy
from base import ip, port, LOCALHOST_IP

__all__ = ['getBroker', 'getMotionProxy', 'getSpeechProxy', 'getMemoryProxy', 'getVisionProxy', 'shutdown']

_broker = None
proxies = []
motionProxy = None
speechProxy = None
memoryProxy = None
visionProxy = None

class InitException(Exception):
	pass
	

def init(_ip = None, _port = None):
    global _broker
    if _broker is None:
        if _ip is None: _ip = ip
        if _port is None: _port = port
    	_broker =  ALBroker("pybroker", LOCALHOST_IP, 9999, _ip, _port)

def getBroker():
	if _broker is None:
		raise InitException, "Must initialize the module first."
	return _broker

def getMotionProxy():
	global motionProxy, proxies, _broker
	if _broker is None:
		raise InitException, "Must initialize the module first."
	if motionProxy is None:
		motionProxy = ALProxy("ALMotion")
		proxies.append(motionProxy)
	return motionProxy

def getSpeechProxy():
	global speechProxy, proxies, _broker
	if _broker is None:
		raise InitException, "Must initialize the module first."
	if speechProxy is None:
		speechProxy = ALProxy("ALTextToSpeech")
		proxies.append(speechProxy)
	return speechProxy


def getMemoryProxy():
	global memoryProxy, proxies, _broker
	if _broker is None:
		raise InitException, "Must initialize the module first."
	if memoryProxy is None:
		memoryProxy = ALProxy("ALMemory")
		proxies.append(memoryProxy)
	return memoryProxy


def getVisionProxy():
	global visionProxy, proxies, _broker
	if _broker is None:
		raise InitException, "Must initialize the module first."
	if visionProxy is None:
		visionProxy = ALProxy("vision")
		proxies.append(visionProxy)
	return visionProxy
	

def shutdown():
	pass

