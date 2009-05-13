#!/usr/bin/python

import socket, threading

#import burst
#from burst.consts import *
#from events import *


import messages, listener

__all__ = ['GameController']


UNKNOWN = None


class ListenersPool(object):
    
    def __init__(self):
        self.lock = threading.Lock()
        self.listeners = set()

    def add(self, item):
        self.lock.acquire()
        self.listeners.add(item)
        self.lock.release()

    def __contains__(self, key):
        self.lock.acquire()
        result = key in self.listeners
        self.lock.release()
        return result
    
    def __getitem__(self, key):
        self.lock.acquire()
        result = self.listeners[key]
        self.lock.release()
        return result

    def __iter__(self):
        self.lock.acquire()
        result = list(self.listeners).__iter__() # Move to another container to avoid concurrent access.
        self.lock.release()
        return result

    def __len__(self):
        self.lock.acquire()
        result = len(self.listeners)
        self.lock.release()
        return result



class ServerSocket(threading.Thread):

    def __init__(self, listeners, port=0):
        threading.Thread.__init__(self)
        self.listeners = listeners
        self.lock = threading.Lock()
        self.status = 'created'
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.settimeout(0.1)
        self.server.bind(('',port))
        self.server.listen(5)
        self.status = 'bound'
        print "Listening on ", self.server.getsockname()[1]

    def stop(self):
        self.lock.acquire()
        assert self.status == 'running'
        self.status = 'running and signaled to stop'
        self.lock.release()

    def stopped(self):
        self.lock.acquire()
        result = self.status == 'running and signaled to stop'
        self.lock.release()
        return result

    def run(self):
        self.status = 'running'
        print 'z'
        while not self.stopped():
            try:
                channel, details = self.server.accept()
                channel.setblocking(False)
                newListener = listener.Listener(channel, details)
                newListener.start()
                self.listeners.add(newListener)
            except socket.timeout:
                pass




class GameController(object):
    
    def __init__(self, port=0):
        self.listeners = ListenersPool()
        self.serverSocket = ServerSocket(self.listeners, port)
            
    def send(self, message, recipient=None):
        messageSent = False        
        if recipient == None:
            messageSent = True # A message to be sent to everyone is considered sent even if "everyone" was an empty set.
            print "sending: ", message, "to", len(self.listeners), "users."
            for listener in self.listeners:
                listener.send(message)
        else:
            for listener in self.listeners:
                if listener.identification == recipient:
                    listener.send(message)
                    messageSent = True
        if not messageSent and DEBUGGING:
            print "[ERROR]: GameController.send - could not deliver a message."

    def run(self):
        self.serverSocket.start()



if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        GameController().run()
    else:
        GameController(int(sys.argv[1])).run()

