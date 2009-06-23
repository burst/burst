#!/usr/bin/python

import player_init
from burst.behavior import InitialBehavior
from burst_events import (EVENT_STEP,
    EVENT_OBSTACLE_SEEN, EVENT_OBSTACLE_LOST, EVENT_OBSTACLE_IN_FRAME)

class SonarTester(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self._eventmanager.register(self.onObstacleSeen, EVENT_OBSTACLE_SEEN)
        self._eventmanager.register(self.onObstacleLost, EVENT_OBSTACLE_LOST)
        self._eventmanager.register(self.onObstacleInFrame, EVENT_OBSTACLE_IN_FRAME)
        # comment out for raw values:
        self._eventmanager.register(self.onStep, EVENT_STEP)

    def onObstacleSeen(self):
        self._actions.say('Obstacle seen!')

        self._lastReading = self._world.robot.sonar.getLastReading()
        self._lastData = self._world.robot.sonar._lastData
        print "Sonar: SEEN obstacle (%s)" % str(self._lastReading)

    def onObstacleLost(self):
        self._actions.say('Obstacle lost!')

    def onObstacleInFrame(self):
        #print 'Obstacle in frame!'
        pass

    def onStep(self):
        print "raw readings: %s" % str(self._world.robot.sonar._lastData)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(SonarTester)
    mainloop.run()
