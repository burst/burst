#!/usr/bin/python


import player_init
from burst.player import Player
from burst.events import *
from burst.consts import *
import burst.moves as moves
from math import cos, sin
import time
from burst.walkparameters import WalkParameters
import os

OUTPUT_FILE_NAME = './testme.txt'
outputFile = None


walkType = 'changeLocationRelative'
walkDistance = 200.0
walkParams = WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           15.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           10.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) 
           -4.5,                  # RHipRoll(degrees)
           0.22,                  # HipHeight(meters)
           3.4,                   # TorsoYOrientation(degrees)
           0.070,                  # StepLength
           0.043,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.00,                  # ZmpOffsetY 
           100])                    # 20ms count per step


class personalWalkManualTweaker(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        self._eventmanager.register(EVENT_FALLEN_DOWN, self.onFallenDown)
        self.walkStartTime = time.time()
        self.test()

    def test(self):
        self._actions.executeHeadMove(moves.BOTTOM_INIT_FAR)
        #self._actions.changeLocationRelative()
        t = getattr(self._actions, walkType)
        t(walkDistance, walk_param=walkParams)
    
    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - took approximately %f seconds." % (self.walkEndTime - self.walkStartTime)
        moduleCleanup(self._eventmanager, self._actions, self._world)
        self._actions.sitPoseAndRelax()
        exit()
#        self._eventmanager.quit()

    def onFallenDown(self):
        print "Fell down."
        moduleCleanup(self._eventmanager, self._actions, self._world)
        self._actions.sitPoseAndRelax()
        exit()



cleaned = False
def moduleCleanup(eventmanager, actions, world):
    global cleaned
    if not cleaned:
        if not robotName is None:
            remaining_steps = world.getRemainingFootstepCount()
            result = str(robotName)
            result += ", " + str(world._memory.getData('Device/SubDeviceList/Battery/Charge/Sensor/Value',0))
            result += ", " + str(walkParams) + ", " + str(walkType) + ", " + str(walkDistance) + ", " 
#            print walkDistance, walkParams[WalkParameters.StepLength], remaining_steps
            distanceWalkedBeforeFallingDown = min(walkDistance, max(0.0, walkDistance - 100 * walkParams[WalkParameters.StepLength] * remaining_steps))
            result += str(distanceWalkedBeforeFallingDown)
#            print "Recording %f as the distance the robot has walked before falling down." % distanceWalkedBeforeFallingDown
            outputFile.write(result+"\n")
        if not outputFile is None and not outputFile.closed:
            outputFile.close()
    cleaned = True


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    #import atexit; atexit.register(moduleCleanup) # Make sure the file is closed down (and thus also flushed) when the program finishes.
    from sys import argv
    OUTPUT_FILE_NAME = os.environ['HOME']+'/src/burst/doc/results_of_personalization_tests.csv'
    #OUTPUT_FILE_NAME = './testme.txt'
    outputFile = open(OUTPUT_FILE_NAME, 'a')

    # Determine the name of the robot you're running on. A bit sideways, I'll admit. Nevertheless:
    robotName = None
    for potentialRobotName in ['hagi', 'messi', 'gerrard', 'raul', 'maldini', 'cech']:
        if potentialRobotName in argv:
            robotName = potentialRobotName
            break
    else:
        print 'Please provide the robot\'s name, so that we can log the test\'s results.'
        exit()
    
    mainloop = MainLoop(personalWalkManualTweaker)
    mainloop.setCtrlCCallback(moduleCleanup)
    mainloop.run()
    #burst.getMotionProxy().getRemainingFootStepCount()

