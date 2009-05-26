#!/usr/bin/python


import socket

import constants
from message import GameControllerMessage


__all__ = ['GameControllerMessage', 'constants', 'GameController']



class GameController(object):

    def __init__(self, gameStatus, host="0.0.0.0", port=3839, bufsize=1024):
        self.gameStatus = gameStatus
        if gameStatus == None: return # When running a robot without an actual game controller.
        self.bufsize = bufsize
        try:
            self.dataGramSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.dataGramSocket.setblocking(False)
            self.dataGramSocket.bind((host,port))
        except socket.error:
            raise Exception("Could not bind the DataGramSocket.")

    def _receive(self):
        try:
            message = self.dataGramSocket.recv(self.bufsize)
            return message
        except socket.error:
            return None

    def calc_events(self, events, deferreds):
        if self.gameStatus == None: return # When running a robot without an actual game controller.
        message = self._receive()
        if not message is None:
            self.gameStatus.readMessage(GameControllerMessage(message))
            self.gameStatus.calc_events(events, deferreds)



if __name__ == '__main__':
    welcome = "Testing the gamecontroller module."
    print len(welcome)*"*" + "\n" + welcome + "\n" + len(welcome)*"*"
    print "No tests have been implemented, thus far."
