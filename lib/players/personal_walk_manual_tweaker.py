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
walkDistance = 100.0
walkParams = moves.SLOW_WALK


class personalWalkManualTweaker(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        self._eventmanager.register(EVENT_FALLEN_DOWN, self.onFallenDown)
        self.walkStartTime = time.time()
        self.test()

    def test(self):
        #self._actions.changeLocationRelative()
        t = getattr(self._actions, walkType)
        t(walkDistance, walk_param=walkParams)
    
    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - took approximately %f seconds." % (self.walkEndTime - self.walkStartTime)
        #self._eventmanager.quit()

    def onFallenDown(self):
        print "FELL DOWN!"
        # Currently, the assuming of a safe state and the setting of the stiffness to off is to be 
        # handled by code in Player itself.
        exit()



def moduleCleanup(eventmanager, actions, world):
    if not robotName is None:
        remaining_steps = world.getRemainingFootstepCount()
        result = str(robotName) + ", " + str(walkParams) + ", " + str(walkType) + ", " + str(walkDistance) + ", " 
        print walkDistance, walkParams[WalkParameters.StepLength], remaining_steps
        distanceWalkedBeforeFallingDown = min(walkDistance, max(0, walkDistance - 100 * walkParams[WalkParameters.StepLength] * remaining_steps))
        result += str(distanceWalkedBeforeFallingDown)
        print "Recording %f as the distance the robot has walked before falling down." % distanceWalkedBeforeFallingDown
        outputFile.write(result+"\n")
    if not outputFile is None and not outputFile.closed:
        outputFile.close()


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

