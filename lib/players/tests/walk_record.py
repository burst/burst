#!/usr/bin/python

from math import pi, sqrt

from datetime import datetime
import os
import sys

# DONT IMPORT BURST BEFORE import player_init
import player_init

from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent
import burst.moves.walks as walks

def pr(s):
    print s

def debugme():
    import pdb; pdb.set_trace()

class WalkRecorder(InitialBehavior):
    """ Use recorder module to record a walk
    """

    WALK_DISTANCE = 40.0
    WALK_PARAMETERS = walks.STRAIGHT_WALK

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        # hack to avoid moving arms with raul's broken RShoulderPitch joint
        if self._world.hostname == 'raul':
            print "on raul - arms will not be moved during walk"
            self._world._motion.setWalkArmsEnable(False)

        now = datetime.now()
        self.startRecord()
        self._actions.changeLocationRelative(
                    self.WALK_DISTANCE, 0.0, 0.0, walk=self.WALK_PARAMETERS).onDone(
                      self.stopRecord)

    def _recordWithWorld(self):
        self._world.startRecordAll('walk_%04d%02d%02d_%02d%02d%02d' % (
            now.year, now.month, now.day, now.hour, now.minute, now.second))

    def _recordWithRecorder(self):
        self.recorder = burst.ALProxy('recorder')
        self.recorder.startRecording()

    def _stopRecordWithWorld(self):
        self._world.stopRecord()

    def _stopRecordWithRecorder(self):
        self.recorder.stopRecording()
        rows = self.recorder.getRowNumber()
        print "recorded %s rows (avg %3.3f Hz)" % (rows, rows/(self._world.time - self._world.start_time))

    startRecord = _recordWithRecorder
    stopRecord_helper = _stopRecordWithRecorder

    def stopRecord(self):
        print "done - stopping recording"
        self.stopRecord_helper()
        self._actions.sitPoseAndRelax()
        self._eventmanager.quit()

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(WalkRecorder).run()

