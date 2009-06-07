import burst_consts as consts
from world.robot import LEDs

class PlayerSettings(object):

    numOfTeamMembers = 3
    numOfTeams = 2

    def __init__(self, world, playerNumber=0, teamColor=0, teamNumber=31): # TODO: Set this to the actual team number we get during the competition.
        self.world = world
        self.playerNumber = playerNumber
        self.teamColor = teamColor
        self.teamNumber = teamNumber
        self.setColors()

    def togglePlayerNumber(self):
        self.playerNumber = (self.playerNumber+1) % PlayerSettings.numOfTeamMembers
        self.setColors()

    def toggleteamColor(self):
        self.teamColor = (self.teamColor+1) % PlayerSettings.numOfTeams
        self.setColors()

    def setColors(self):
        self.world.robot.leds.leftFootLED.turnOn(consts.TeamColors[self.teamColor])
