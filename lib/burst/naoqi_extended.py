import os, sys, time
import socket


from burst_util import WrapWithDeferreds

# wrapped to allow import from pynaoqi
try:
    from naoqi import ALBroker, ALProxy
except:
    pass
from options import host_to_ip, LOCALHOST_IP
import burst

__all__ = ['getBroker', 'getMotionProxy', 'getSpeechProxy', 'getMemoryProxy', 'getVisionProxy', 'getDCMProxy', 'shutdown']

_broker = None
proxies = [] # This was added for use by shutdown(). If no longer useful by the time we're done, we should get rid of this.
motionProxy = None
speechProxy = None
memoryProxy = None
visionProxy = None
dcmProxy = None

# TODO: Move to burst_exceptions
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
        if ip is not None: burst.ip = host_to_ip(ip)
        if port is not None: burst.port = port
        local_port = get_first_available_tcp_port(10234)
        try:
            _broker =  ALBroker('burst%s' % local_port, LOCALHOST_IP, local_port, burst.ip, burst.port)
        except Exception, e:
            print "connection failed - burst not init"
            _broker = None
            raise

def getBroker():
    global _broker
    if _broker is None:
        raise InitException, "Must initialize the module first."
    return _broker

def getMotionProxy(deferred = False):
    global motionProxy, proxies, _broker
    if _broker is None:
        raise InitException, "Must initialize the module first."
    if motionProxy is None:
        motionProxy = ALProxy("ALMotion")
        proxies.append(motionProxy)
    if deferred:
        motionProxy = WrapWithDeferreds(motionProxy)
    return motionProxy

def getSpeechProxy(deferred = False):
    global speechProxy, proxies, _broker
    if _broker is None:
        raise InitException, "Must initialize the module first."
    if speechProxy is None:
        try:
            speechProxy = ALProxy("ALTextToSpeech")
            proxies.append(speechProxy)
        except Exception,e :
            print "WARNING: Speech Proxy not available (Exception: %s)" % e
    if deferred:
        speechProxy = WrapWithDeferreds(speechProxy)
    return speechProxy


def getMemoryProxy(deferred = False):
    global memoryProxy, proxies, _broker
    if _broker is None:
        raise InitException, "Must initialize the module first."
    if memoryProxy is None:
        memoryProxy = ALProxy("ALMemory")
        proxies.append(memoryProxy)
    if deferred:
        memoryProxy = WrapWithDeferreds(memoryProxy)
    return memoryProxy


def getVisionProxy(deferred = False):
    global visionProxy, proxies, _broker
    if _broker is None:
        raise InitException, "Must initialize the module first."
    if visionProxy is None:
        visionProxy = ALProxy("vision")
        proxies.append(visionProxy)
    if deferred:
        visionProxy = WrapWithDeferreds(visionProxy)
    return visionProxy
    
def getDCMProxy(deferred = False):
    global dcmProxy, proxies, _broker
    if _broker is None:
        raise InitException, "Must initialize the module first."
    if dcmProxy is None:
        dcmProxy = ALProxy("DCM")
        proxies.append(dcmProxy)
    if deferred:
        dcmProxy = WrapWithDeferreds(dcmProxy)
    return dcmProxy


def shutdown():
    pass

