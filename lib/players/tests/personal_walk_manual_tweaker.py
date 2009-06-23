#!/usr/bin/python


import player_init
from burst_util import DeferredList
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves as moves
import time
from burst.walkparameters import WalkParameters
from burst.moves.walks import Walk
import os


class PersonalWalkManualTweaker(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)
        #self._eventmanager.register(EVENT_FALLEN_DOWN, self.onFallenDown)
        self.walkStartTime = time.time()
        self.test()

    def test(self):
        time.sleep(3)
        self._actions.executeHeadMove(moves.HEAD_MOVE_FRONT_FAR)
        #self._actions.changeLocationRelative()
        t = getattr(self._actions, walkType)
        t(walkDistance, walk=walkParams)

    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - took approximately %f seconds." % (self.walkEndTime - self.walkStartTime)
        moduleCleanup(self._eventmanager, self._actions, self._world)
        self._actions.sitPoseAndRelax()
        exit()
#        self._eventmanager.quit()

#    def onFallenDown(self):
#        print "Fell down."
#        moduleCleanup(self._eventmanager, self._actions, self._world)
#        self._actions.sitPoseAndRelax()
#        exit()

cleaned = False
def moduleCleanup(eventmanager, actions, world):
    global cleaned
    def onResults(results):
        remaining_steps = results[0][1]
        battery_charge = results[1][1]
        global cleaned
        if not cleaned:
            if not robotName is None:
                result = str(robotName)
                result += ", " + str(battery_charge)
                result += ", " + str(walkParams) + ", " + str(walkType) + ", " + str(walkDistance) + ", "
    #            print walkDistance, walkParams[WalkParameters.StepLength], remaining_steps
                distanceWalkedBeforeFallingDown = min(walkDistance, max(0.0, walkDistance - 100 * walkParams[WalkParameters.StepLength] * remaining_steps))
                result += str(distanceWalkedBeforeFallingDown)
    #            print "Recording %f as the distance the robot has walked before falling down." % distanceWalkedBeforeFallingDown
                outputFile.write(result+"\n")
            if not outputFile is None and not outputFile.closed:
                outputFile.close()
        cleaned = True
    d = None
    if not cleaned:
        d = DeferredList([world.getRemainingFootstepCount(),
            world._memory.getData('Device/SubDeviceList/Battery/Charge/Sensor/Value',0)])
        d.addCallback(onResults)
    return d

if __name__ == '__main__':
#    time.sleep(3)
    import burst
    from burst.eventmanager import MainLoop
    #import atexit; atexit.register(moduleCleanup) # Make sure the file is closed down (and thus also flushed) when the program finishes.
    from sys import argv
    OUTPUT_FILE_NAME = os.environ['HOME']+'/src/burst/data/calibration/results_of_personalization_tests.csv'
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

    mainloop = MainLoop(PersonalWalkManualTweaker)
    mainloop.setCtrlCCallback(moduleCleanup)
    mainloop.run()
    #burst.getMotionProxy().getRemainingFootStepCount()

