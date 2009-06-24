import burst_consts as consts
import burst
from world.robot import LEDs

class PlayerSettings(object):

    numOfTeamMembers = 3
    numOfTeams = 2

    def __init__(self, world, teamColor=0, teamNumber=consts.BURST_TEAM_NUMBER):
        self.world = world
        self.playerNumber = burst.options.jersey
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

