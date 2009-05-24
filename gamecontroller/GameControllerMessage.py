#!/usr/bin/python

# TODO:
# Odd: I'm being sent 0 for firstHalf if it's either the second half or a penalty shoot for b, and 1 in both other cases.

import socket, struct

InitialGameState = 0; ReadyGameState = 1; SetGameState = 2; PlayGameState = 3; FinishGameState = 4;
TeamA = 0; TeamB = 1;


class GameControllerMessage(object):

    def __init__(self, string):
        self.string = string

    def getHeader(self):
        return self.string[0:4]

    def getVersion(self):
        return struct.unpack("I", self.string[4:8])[0]

    def getPlayersPerTeam(self):
        return ord(self.string[8])

    def getGameState(self): # TODO: Think about the enum.
        return ord(self.string[9])

    def getIsFirstHalf(self):
        return ord(self.string[10]) != 0

    def getKickOffTeamNumber(self):
        return ord(self.string[11])

    def getIsSecondaryState(self):
        return ord(self.string[12]) # TODO: WTF is this?

    def getDropInTeamNumber(self): # TODO: Appears to be somehow connected to the "Out By Red/Blue" button.
        return ord(self.string[13])

    def getDropInTime(self): # TODO: 1. -1 signals no drop in time, or something. 2. Not really sure what anything else means. The time SINCE the D.I.?
        return struct.unpack("h", self.string[14:16])[0]

    def getSecondsRemaining(self):
        return struct.unpack("I", self.string[16:20])[0]

    def getTeamNumber(self, team):
        return ord(self.string[20+team*(4+11*4)])

    def getTeamColor(self, team): # TODO: Appears to be constant.
        return ord(self.string[21+team*(4+11*4)])

    def getTeamScore(self, team):
        start = 22 + team*(4+11*4)
        return struct.unpack("h", self.string[start:start+2])[0]

    def getPenaltyStatus(self, team, player):
        start = 24 + team*(4+11*4) + 4*(player-1)
        return struct.unpack("h", self.string[start:start+2])[0]

    def getPenaltyTimeRemaining(self, team, player):
        start = 26 + team*(4+11*4) + 4*(player-1)
        return struct.unpack("h", self.string[start:start+2])[0]


host = "0.0.0.0"
port = 3839
buf = 1024
addr = (host,port)

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#UDPSock.setblocking(False)
UDPSock.bind(addr)
while True:
    try:
        data,addr = UDPSock.recvfrom(buf)
        x = GameControllerMessage(data)
        a, b = 1, 3
        print x.getPenaltyStatus(a, b), x.getPenaltyTimeRemaining(a, b)
#        print x.getTeamScore(1)
    except socket.error:
        pass


'''

0-3: header
4-7: version
8: playersPerTeam
9: state
10: firstHalf
11: kickOffTeam
12: secondaryState
13: dropInTeam
14-15: dromInTime
16-19: secsRemaining
20: first team num
21: first team color
22-23: first time score
24-25: first team first player penaly type
26-27: first team first player penalty time
28-29: first team second player penalty type
30-31: first team second player penalty time
32-33: first team third player penalty type
34-35: first team third player penalty time
36: second team num
'''

