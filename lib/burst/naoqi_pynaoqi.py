"""
Give the same interface as naoqi_extended using pynaoqi
"""

import pynaoqi

con = pynaoqi.getDefaultConnection()

def getDCMProxy(deferred = False):
    return con.DCM

def getMemoryProxy(deferred = False):
    return con.ALMemory

def getMotionProxy(deferred = False):
    return con.ALMotion

def getLedsProxy(deferred = False):
    return con.ALLeds

def getSonarProxy(deferred = False):
    return con.ALSonar

def getBroker():
    """ this is BROKEN """
    return None

def getSpeechProxy(deferred = False):
    """ return None if nothing there """
    return hasattr(con, 'ALTextToSpeech') and con.ALTextToSpeech or None

def getALVideoDeviceProxy(deferred = False):
    return con.ALVideoDevice

def getBurstMemProxy(deferred = False):
    return con.burstmem

def getImopsProxy(deferred = False):
    return hasattr(con, 'imops') and con.imops or None

def getSentinelProxy(deferred = False):
    return con.ALSentinel

