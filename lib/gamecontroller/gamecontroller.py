#import burst
#from burst.consts import *
#from events import *

import messages

__all__ = ['GameController']


DEBUGGING = True


# State of the game:
GameStateInitial = 0;
GameControllerInitialState = 3

# States for any given robot:



class GameController(object):
    
    def __init__(self, listeners=set(), currentState=GameControllerInitialState):
        self.listeners = set([listener for listener in listeners])
            
    def addListener(self, listener):
        self.add(listener)

    def addListeners(self, listeners):
        self.listeners.update(listeners)

    def sendMessage(self, message, recipient=None):
        messageSent = False        
        if recipient == None:
            messageSent = True
            for listener in self.listeners:
                listener.sendMessage(message)
        else:
            for listener in self.listeners:
                if listener.identification == recipient:
                    listener.sendMessage(message)
                    messageSent = True
        if not messageSent and DEBUGGING:
            print "[ERROR]: GameController.sendMessage - could not deliver a message."

