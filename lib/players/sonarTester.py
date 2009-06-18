#!/usr/bin/python

import player_init
from burst.player import Player
from burst.events import (EVENT_SONAR_OBSTACLE_SEEN, EVENT_SONAR_OBSTACLE_LOST, EVENT_SONAR_OBSTACLE_IN_FRAME)

class SonarTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        
        self._eventmanager.register(self.onObstacleSeen, EVENT_SONAR_OBSTACLE_SEEN)
        self._eventmanager.register(self.onObstacleLost, EVENT_SONAR_OBSTACLE_LOST)
        self._eventmanager.register(self.onObstacleInFrame, EVENT_SONAR_OBSTACLE_IN_FRAME) 
        
    def onObstacleSeen(self):
        self._actions.say('Obstacle seen!')
        
        self._lastReading = self._eventmanager._world.robot.sonars.getLastReading()
        print "SONAR: SEEN obstacle (on %s, distance of %f)" % (self._lastReading)
        
    def onObstacleLost(self):
        self._actions.say('Obstacle lost!')

    def onObstacleInFrame(self):
        #print 'Obstacle in frame!'
        pass

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(SonarTester)
    mainloop.run()
