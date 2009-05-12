

import messages


class Listener(object):
    
    def __init__(self, teamColor, robotNumber, ip, port):
        self.identification = (teamColor, robotNumber)
        self.teamColor = teamColor
        self.robotNumber = robotNumber
        self.ip = ip
        self.port = port
        self.connected = False
        self.connect()

    def connect(self):
        self.connected = True
        pass

    def disconnect(self):
        pass

    def send(self, message):
        if not self.connected:
            raise Exception("Trying to send a message to a listener (robot) without first being connected to it.")
        else:
            serializedMessage = message.serialize()
            # Put it through the TCP socket.
            pass

    def affectsMe(self, message):
        if message.affectedTeam == messages.BOTH_TEAMS:
            return True
        elif message.affectedTeam == self.teamColor:
            return message.affectedRobot == self.robotNumber or message.affectedRobot == messages.ALL_ROBOTS_OF_AFFECTED_TEAM
        else:
            return False
    


