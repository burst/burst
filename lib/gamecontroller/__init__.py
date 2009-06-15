#!/usr/bin/python


import socket

import constants
import burst_consts # sorry, should not be here - but I find a single consts file easier.
from message import GameControllerMessage


__all__ = ['GameControllerMessage', 'constants', 'GameController', 'EmptyGameController']



class GameController(object):

    def __init__(self, gameStatus, host="0.0.0.0",
            port=burst_consts.GAME_CONTROLLER_BROADCAST_PORT, bufsize=1024):
        self.gameStatus = gameStatus
        self.bufsize = bufsize
        try:
            self.dataGramSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.dataGramSocket.setblocking(False)
            self.dataGramSocket.bind((host,port))
        except socket.error:
            raise Exception("Could not bind the DataGramSocket.")

    def shutdown(self):
        self.dataGramSocket.close()

    def _receive(self):
        try:
            message = self.dataGramSocket.recv(self.bufsize)
            return message
        except socket.error:
            return None

    def calc_events(self, events, deferreds):
        message = self._receive()
        if not message is None:
            self.gameStatus.readMessage(GameControllerMessage(message))



class EmptyGameController(object):
    '''
    An empty implementation of GameController, for those who want to run their programs without the game controller.
    '''
    def __init__(*args, **kw): pass
    def shutdown(*args, **kw): pass
    def calc_events(*args, **kw): pass



if __name__ == '__main__':
    welcome = "Testing the gamecontroller module."
    print len(welcome)*"*" + "\n" + welcome + "\n" + len(welcome)*"*"
    print "No tests have been implemented, thus far."

