import burst_consts as consts


class PlayerSettings(object):

    numOfTeamMembers = 3
    numOfTeams = 2

    def __init__(self, playerNumber=0, teamColor=0, teamNumber=31): # TODO: Set this to the actual team number we get during the competition.
        self.playerNumber = playerNumber
        self.teamColor = teamColor
        self.teamNumber = teamNumber

    def togglePlayerNumber(self):
        self.playerNumber = (self.playerNumber+1) % PlayerSettings.numOfTeamMembers

    def toggleteamColor(self):
        self.teamColor = (self.teamColor+1) % PlayerSettings.numOfTeams
