import os, sys, time
import socket

import motion

from naoqi import ALBroker, ALProxy
from base import host_to_ip, LOCALHOST_IP
import base

__all__ = ['getBroker', 'getMotionProxy', 'getSpeechProxy', 'getMemoryProxy', 'getVisionProxy', 'shutdown']

_broker = None
proxies = []
motionProxy = None
speechProxy = None
memoryProxy = None
visionProxy = None

class InitException(Exception):
    pass
    
def get_first_available_tcp_port(start_number, host='127.0.0.1'):
    number = start_number
    s = socket.socket()
    while number < 65535:
        try:
            s.bind((host, number))
            s.close()
            break
        except:
            number += 1
    return number

def init(ip = None, port = None):
    """ You must call this first. Technically, we could init everything
    the first time it is called, but we prefer to make you call this
    function first. Just because we can.
    
        Signed: The doc string writer.
    """
    global _broker
    if _broker is None:
        if ip is not None: base.ip = host_to_ip(ip)
        if port is not None: base.port = port
        local_port = get_first_available_tcp_port(10234)
        _broker =  ALBroker("pybroker", LOCALHOST_IP, local_port, base.ip, base.port)

def getBroker():
    global _broker
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

