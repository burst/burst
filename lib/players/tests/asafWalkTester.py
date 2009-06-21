#!/usr/bin/python

# DON'T PUT ANYTHING BEFORE THIS LINE
import player_init

from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves as moves
from math import cos, sin
import time

# aldebaran motion constants - need to import player_init and burst first
import motion

class walkTester(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.kp = None
        self._eventmanager.register(self.onChangeLocationDone, EVENT_CHANGE_LOCATION_DONE)        
        self.walkStartTime = time.time()
        self.doWalk()

    def doWalk(self):
        readyStand = [0.065920039999999999,
             -0.65199196000000004,
             1.7471840000000001,
             0.25460203999999997,
             -1.5662560000000001,
             -0.33130205000000001,
             -0.012313961999999999,
             0.0072991871,
             0.0061779618000000003,
             -0.0076280384999999999,
             -0.78536605999999998,
             1.5431621,
             -0.78238200999999996,
             0.016915962,
             0.0061779618000000003,
             0.072139964000000001,
             -0.77931397999999996,
             1.53711,
             -0.79303604000000005,
             -0.073590039999999995,
             1.734996,
             -0.25008397999999998,
             1.5646381,
             0.36053199000000002,
             0.019900039000000001,
             0.0014810241000000001]

        motionProxy = self._actions._motion
        motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
        
        print motionProxy.getBodyStiffnesses()
        # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
        motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 20.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
        motionProxy.setWalkArmsEnable(True)

        # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
        motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.19, 2.0 )
        # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
        motionProxy.setWalkConfig( 0.015, 0.015, 0.04, 0.3, 0.015, 0.015)
        motionProxy.addWalkStraight(0.05, 150)
        motionProxy.addWalkStraight(0.05, 125)
#        motionProxy.addWalkStraight(0.44, 21)
        motionProxy.gotoBodyAnglesWithSpeed(readyStand,20,1)
#        time.sleep(3)
        motionProxy.walk()

    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - tool approximately %f" % (self.walkEndTime - self.walkStartTime)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(walkTester).run()

