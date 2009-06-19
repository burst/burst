#!/usr/bin/python


import socket

import gamecontroller_consts as constants
import burst_consts # sorry, should not be here - but I find a single consts file easier.
from message import GameControllerMessage


__all__ = ['GameControllerMessage', 'constants', 'GameController', 'EmptyGameController']



class GameController(object):

    def __init__(self, gameStatus, host="0.0.0.0",
            port=burst_consts.GAME_CONTROLLER_BROADCAST_PORT, bufsize=1024):
        self.gameStatus = gameStatus
        self.bufsize = bufsize
        self._socket_bound = False
        try:
            self.dataGramSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.dataGramSocket.setblocking(False)
            self.dataGramSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dataGramSocket.bind((host,port))
            self._socket_bound = True
        except socket.error:
            print "ERROR: GameController: Cannot bind to socket (%s)" % ((host, port),)

    def shutdown(self):
        if self._socket_bound:
            self.dataGramSocket.close()
            self._socket_bound = False

    def _receive(self):
        if not self._socket_bound: return
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

