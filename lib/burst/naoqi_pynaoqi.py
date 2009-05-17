"""
Give the same interface as naoqi_extended using pynaoqi
"""

import pynaoqi

con = pynaoqi.getDefaultConnection()

def getMemoryProxy():
    return con.ALMemory

def getMotionProxy():
    return con.ALMotion

def getBroker():
    """ this is BROKEN """
    return con

def getSpeechProxy():
    """ return None if nothing there """
    return hasattr(con, 'ALTextToSpeech') and con.ALTextToSpeech or None

