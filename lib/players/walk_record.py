#!/usr/bin/python

from math import pi, sqrt

from datetime import datetime
import os
import sys

in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *
from burst.consts import *
from burst.eventmanager import AndEvent, SerialEvent
import burst.moves as moves

def pr(s):
    print s

def debugme():
    import pdb; pdb.set_trace()

class Rectangle(Player):
    
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
        print "recorded %s rows (avg %3.3f Hz)" % (rows, rows/(self._world.time - self._world.const_time))

    startRecord = _recordWithRecorder
    stopRecord_helper = _stopRecordWithRecorder

    def onStart(self):

        # hack to avoid moving arms with raul's broken RShoulderPitch joint
        if self._world.hostname == 'raul':
            print "on raul - arms will not be moved during walk"
            self._world._motion.setWalkArmsEnable(False)

        now = datetime.now()
        self.startRecord()
        self._actions.initPoseAndStiffness()
        self._actions.changeLocationRelative(
                    40.0, 0.0, 0.0, walk_param=moves.SLOW_WALK).onDone(
                      self.stopRecord)

    def stopRecord(self):
        print "done - stopping recording"
        self.stopRecord_helper()
        self._actions.sitPoseAndRelax()
        self._eventmanager.quit()

    def onStop(self):
        super(Rectangle, self).onStop()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import EventManagerLoop
    burst.init()
    EventManagerLoop(Rectangle).run()

