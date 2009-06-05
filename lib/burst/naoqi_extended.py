import os, sys, time
import socket


from burst_util import (WrapWithDeferreds,
    get_first_available_tcp_port, once)

# wrapped to allow import from pynaoqi
try:
    from naoqi import ALBroker, ALProxy
except:
    pass
from options import host_to_ip, LOCALHOST_IP
import burst

__all__ = ['getBroker', 'getMotionProxy', 'getSpeechProxy', 'getMemoryProxy', 'getVisionProxy', 'getDCMProxy', 'shutdown'
    ,'getLedsProxy', 'getUltraSoundProxy']

_broker = None
proxies = [] # This was added for use by shutdown(). If no longer useful by the time we're done, we should get rid of this.
motionProxy = None
speechProxy = None
memoryProxy = None
visionProxy = None
dcmProxy = None
ledsProxy = None
ultraSoundProxy = None

# TODO: Move to burst_exceptions
class InitException(Exception):
    pass
    
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

class MissingProxy(object):
    """ Wrapper to a proxy object that does nothing, here
    to allow DCM tests by vova without drastic changes
    to the rest of the library.
    """

    def __init__(self, name):
        self._name = name
        if not 'post' in name:
            self.post = MissingProxy('%s.post' % self._name)

    def __getattr__(self, k):
        #print "missing %s.%s" % (self._name, k)
        return lambda *args, **kw: None

def getProxy(proxy_name, global_name, deferred):
    global proxies, _broker
    if _broker is None:
        raise InitException, "Must initialize the module first."
    gs = globals()
    if gs[global_name] is None:
        try:
            proxy = ALProxy(proxy_name)
        except Exception, e:
            proxy = MissingProxy(proxy_name)
            print "WARNING: %s module is not available (Exception: %s)" % (proxy_name, e)
        if deferred:
            proxy = WrapWithDeferreds(proxy)
        proxies.append(proxy)
    gs[global_name] = proxy
    return proxy

for getter, global_name, proxy_name in [
    ('getMotionProxy', 'motionProxy', 'ALMotion'),
    ('getSpeechProxy', 'speechProxy', 'ALTextToSpeech'),
    ('getLedsProxy',   'ledsProxy',   'ALLeds'),
    ('getMemoryProxy', 'memoryProxy', 'ALMemory'),
    ('getVisionProxy', 'visionProxy', 'vision'),
    ('getDCMProxy',    'dcmProxy',    'DCM'),
    ('getUltraSoundProxy', 'ultraSoundProxy', 'ALUltraSound')]:
    globals()[getter] = once(
        lambda deferred, proxy_name=proxy_name, global_name=global_name:
            getProxy(proxy_name, global_name, deferred))

def shutdown():
    pass

