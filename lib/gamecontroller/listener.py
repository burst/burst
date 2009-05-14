#!/usr/bin/python

import threading

import messages

__all__ = ['Listener']


class Listener(threading.Thread):
    
    def __init__(self, channel, details):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.inbuffer = ''
        self.channel = channel
        self.details = details
        self.isReady = False
        self.start()

    def ready(self):
        self.lock.acquire()
        result = self.isReady
        self.lock.release()
        return result

    def setReady(self, isReady):
        self.lock.acquire()
        self.isReady = isReady
        self.lock.release()

    def send(self, message):
        self.channel.send(message.serialize())

    # TODO: I don't think I need the following function anymore.
    def affectedBy(self, message):
        if message.affectedTeam == messages.BOTH_TEAMS:
            return True
        elif message.affectedTeam == self.teamColor:
            return message.affectedRobot == self.robotNumber or message.affectedRobot == messages.ALL_ROBOTS_OF_AFFECTED_TEAM
        else:
            return False

    def handshake(self):
        print "sending REPORT command"
        self.channel.send("REPORT!")
        self.channel.setblocking(True)
        while not '\n' in self.inbuffer:
            self.inbuffer += self.channel.recv(100)
        firstLine, self.inbuffer = tuple(self.inbuffer.split('\n',1))
        self.channel.setblocking(False)
        return tuple(int(firstLine.split(' ',1)[0]), int(firstLine.split(' ',1)[1]))

    def run(self):
        self.teamColor, self.robotNumber = self.handshake()
        self.identification = (self.teamColor, self.robotNumber)
        self.setReady(True)

