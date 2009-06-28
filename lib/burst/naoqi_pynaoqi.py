"""
Give the same interface as naoqi_extended using pynaoqi
"""

from burst_consts import (SONAR_MODULE, VIDEO_MODULE,
    BURST_SHARED_MEMORY_PROXY_NAME)
import pynaoqi

def getDCMProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return con.DCM

def getMemoryProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return con.ALMemory

def getMotionProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return con.ALMotion

def getLedsProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return con.ALLeds

def getSonarProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return getattr(con, SONAR_MODULE)

def getBroker():
    """ this is BROKEN """
    return None

def getSpeechProxy(deferred = False):
    """ return None if nothing there """
    con = pynaoqi.getDefaultConnection()
    return hasattr(con, 'ALTextToSpeech') and con.ALTextToSpeech or None

def getALVideoDeviceProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return getattr(con, VIDEO_MODULE)

def getBurstMemProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return getattr(con, BURST_SHARED_MEMORY_PROXY_NAME)

def getImopsProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return hasattr(con, 'imops') and con.imops or None

def getSentinelProxy(deferred = False):
    con = pynaoqi.getDefaultConnection()
    return con.ALSentinel if hasattr(con, 'ALSentinel') else None

