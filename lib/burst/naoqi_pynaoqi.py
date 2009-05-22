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

def getBroker():
    """ this is BROKEN """
    return con

def getSpeechProxy(deferred = False):
    """ return None if nothing there """
    return hasattr(con, 'ALTextToSpeech') and con.ALTextToSpeech or None

