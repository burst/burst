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

def getUltraSoundProxy(deferred = False):
    return con.ALUltraSound

def getBroker():
    """ this is BROKEN """
    return None

def getSpeechProxy(deferred = False):
    """ return None if nothing there """
    return hasattr(con, 'ALTextToSpeech') and con.ALTextToSpeech or None

def getNaoCamProxy(deferred = False):
    return con.NaoCam

def getBurstMemProxy(deferred = False):
    return con.burstmem

def getImopsProxy(deferred = False):
    return con.imops

def getSentinelProxy(deferred = False):
    return con.ALSentinel

