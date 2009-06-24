import burst_consts
import burst
from world.robot import LEDs

class PlayerSettings(object):

    numOfTeamMembers = 3
    numOfTeams = 2

    def __init__(self, world):
        self.world = world
        self.playerNumber = burst.options.jersey - 1 # XXX - Jersey is 1-based, PlayerNumber is 0-based
        self.teamColor = burst.options.starting_team_color
        self.teamNumber = burst_consts.BURST_TEAM_NUMBER
        self.setColors()

    def togglePlayerNumber(self):
        self.playerNumber = (self.playerNumber+1) % PlayerSettings.numOfTeamMembers
        self.setColors()

    def toggleteamColor(self):
        self.teamColor = (self.teamColor+1) % PlayerSettings.numOfTeams
        self.setColors()

    def setColors(self):
        self.world.robot.leds.leftFootLED.turnOn(burst_consts.TeamColors[self.teamColor])

    def __str__(self):
        return '<PlayerSettings color=%s team#=%d player#=%d>' % (
            burst_consts.team_color_str(self.teamColor), self.teamNumber, self.playerNumber)
    __repr__ = __str__
