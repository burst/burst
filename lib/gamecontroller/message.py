#!/usr/bin/python

# TODO:
# Odd: I'm being sent 0 for firstHalf if it's either the second half or a penalty shoot for b, and 1 in both other cases.

import socket, struct

# TODO: This is compatible with my reverse engineering of the Java GameController. Is it also compatible with the header in
# ~/src/burst/gamecontroller/GameController2006/sample/GameController/GameController/RoboCupGameControlData.h ?



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
        GameControllerMessage._validateTeam(team)
        return ord(self.string[20+team*(4+11*4)])

    def getTeamColor(self, team): # TODO: Appears to be constant.
        GameControllerMessage._validateTeam(team)
        return ord(self.string[21+team*(4+11*4)])

    def getTeamScore(self, team):
        GameControllerMessage._validateTeam(team)
        start = 22 + team*(4+11*4)
        return struct.unpack("h", self.string[start:start+2])[0]

    def getPenaltyStatus(self, team, player):
        GameControllerMessage._validateTeam(team)
        GameControllerMessage._validatePlayer(player)
        start = 24 + team*(4+11*4) + 4*(player-1)
        return struct.unpack("h", self.string[start:start+2])[0]

    def getPenaltyTimeRemaining(self, team, player): # TODO: Change this to status
        GameControllerMessage._validateTeam(team)
        GameControllerMessage._validatePlayer(player)
        start = 26 + team*(4+11*4) + 4*(player-1)
        return struct.unpack("h", self.string[start:start+2])[0]

    @staticmethod
    def _validateTeam(team):
        if not 0 <= team <= 1:
            raise Exception("Legal teams: 0, 1. Got: " + str(team))

    @staticmethod
    def _validatePlayer(player):
        if not 1 <= player <= 11:
            import pdb; pdb.set_trace()
            raise Exception("Legal players: 1-11. Got: " + str(player))

if __name__ == '__main__':
    welcome = 'Testing the GameControllerMessage module.'
    print len(welcome)*'*' + '\n' + welcome + '\n' + len(welcome)*'*'
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
            a, b = 0, 1
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

