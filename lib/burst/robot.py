import os, sys, time
import motion

from naoqi import ALBroker, ALProxy
from base import ip, port, LOCALHOST_IP

__all__ = ['getBroker', 'getMotionProxy', 'getSpeechProxy']

_broker = None
proxies = []
motionProxy = None
speechProxy = None

def init(_ip = None, _port = None):
    global _broker
    if _broker is None:
        if _ip is None: _ip = ip
        if _port is None: _port = port
    	_broker =  ALBroker("pybroker", LOCALHOST_IP, 9999, _ip, _port)

def getBroker():
	return _broker

def getMotionProxy():
	global motionProxy
	global proxies
	if motionProxy is None:
		motionProxy = ALProxy("ALMotion")
		proxies.append(motionProxy)
	return motionProxy

def getSpeechProxy():
	global speechProxy
	global proxies
	if speechProxy is None:
		speechProxy = ALProxy("ALTextToSpeech")
		proxies.append(speechProxy)
	return speechProxy

def shutdown():
	pass

