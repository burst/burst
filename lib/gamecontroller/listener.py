#!/usr/bin/python

import threading

import messages

UNKNOWN = None

__all__ = ['Listener']

class Listener(threading.Thread):
    
    def __init__(self, channel, details):
        threading.Thread.__init__(self)
        self.channel = channel
        self.details = details
        self.identification = (UNKNOWN, UNKNOWN)
        self.teamColor = UNKNOWN
        self.robotNumber = UNKNOWN
        self.connected = False

    def send(self, message):
        print str(self.details) + ": " + str(message)
        if not self.connected:
            pass
#            raise Exception("Trying to send a message to a listener (robot) without first being connected to it.")
        else:
            serializedMessage = message.serialize()
            # Put it through the TCP socket.
            print 'ook', str(message)
            pass
        self.channel.send(str(message))

    def affectsMe(self, message):
        if message.affectedTeam == messages.BOTH_TEAMS:
            return True
        elif message.affectedTeam == self.teamColor:
            return message.affectedRobot == self.robotNumber or message.affectedRobot == messages.ALL_ROBOTS_OF_AFFECTED_TEAM
        else:
            return False



