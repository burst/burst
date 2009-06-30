#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst.behavior import InitialBehavior
import burst.moves.poses as poses
import burst
from burst_consts import SECONDARY_ATTACK_ON_LEFT, SECONDARY_JERSEY
from burst_consts import LEFT, RIGHT

class Kicker(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.STRAIGHT_WALK_INITIAL_POSE)

    def _start(self, firstTime=False):
        if self._world.robot.jersey == SECONDARY_JERSEY:
            self._ballkicker = self.secondary()
            self._ballkicker.onDone(self.kick).onDone(self.onKickComplete)
        #        jersey = self._world.robot.jersey
        #        kickOffTeamColor = main._world.gameStatus.kickOffTeam
        #        ourTeamColor = main._world.gameStatus.mySettings.teamColor
        #        weAreKickTeam = ourTeamColor == kickOffTeamColor
        #        print "We are kick off team: %s" % weAreKickTeam

        else:
            self._ballkicker = self.kick()
            self._ballkicker.onDone(self.onKickComplete)

    def _stop(self):
        return self._ballkicker.stop()

    def kick(self):
        #print init started
        target_left_right_posts = [self._world.opposing_lp, self._world.opposing_rp]
        return self._actions.kickBall(target_left_right_posts=target_left_right_posts)

    def onKickComplete(self):
        print "kick complete - currently Player will restart me, just let it."
        self.stop()
        
    def secondary(self):
        direction = 1 - SECONDARY_ATTACK_ON_LEFT
        return self._actions.runSecondary(direction=direction)
    
    def initKick(self):
        #target_left_right_posts = [self._world.opposing_lp, self._world.opposing_rp]
        return self._actions.kickInit(side=LEFT)

    def onInitKickComplete(self):
        self._ballkicker = self.kick()
        self._ballkicker.onDone(self.onKickComplete)
        print "init kick complete - currently Player will restart me, just let it."
        #self.stop()

if __name__ == '__main__':
    from burst.eventmanager import MainLoop
    MainLoop(Kicker).run()

