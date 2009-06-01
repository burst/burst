#!/usr/bin/python

# DON'T PUT ANYTHING BEFORE THIS LINE
import player_init

from burst.player import Player
from burst.events import *
from burst.consts import *
import burst.moves as moves
from math import cos, sin
import time

# aldebaran motion constants - need to import player_init and burst first
import motion

class walkTester(Player):
    
#    def onStop(self):
#        super(Kicker, self).onStop()

    def onStart(self):
        self.kp = None

        self._actions.initPoseAndStiffness().onDone(self.doWalk)

    def doWalk(self):
        motionProxy = self._actions._motion
        motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
        # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
        #new walk
        motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 20.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
        #old walk
        #motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD ) 
        motionProxy.setWalkArmsEnable(True)

        # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
        motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.18, 5.0 )
        # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
        motionProxy.setWalkConfig( 0.02, 0.015, 0.04, 0.3, 0.015, 0.02 )
        #motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
        time.sleep(4)
        motionProxy.addWalkStraight( 0.02*12, 23)
        #motionProxy.addWalkStraight( 0.02*16, 20)
        #motionProxy.addWalkStraight( 0.02*2, 23)
        #motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.19, 5.0 )
        #motionProxy.addWalkStraight( 0.025*4, 122)
        motionProxy.walk()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(walkTester).run()

