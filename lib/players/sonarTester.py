#!/usr/bin/python

import player_init
from burst.player import Player
from burst.events import (EVENT_SONAR_OBSTACLE_CENTER, EVENT_SONAR_OBSTACLE_LEFT, EVENT_SONAR_OBSTACLE_RIGHT)

class SonarTester(Player):
    
    def onStart(self):
        self._actions.initPoseAndStiffness()
        
        self._eventmanager.register(self.onObstacleCenter, EVENT_SONAR_OBSTACLE_CENTER)
        self._eventmanager.register(self.onObstacleLeft, EVENT_SONAR_OBSTACLE_LEFT)
        self._eventmanager.register(self.onObstacleRight, EVENT_SONAR_OBSTACLE_RIGHT) 
        
    def onObstacleCenter(self):
        print 'Obstacle at center!'
        self._actions.say('Obstacle at center!')
        
    def onObstacleLeft(self):
        print 'Obstacle at left!'
        self._actions.say('Obstacle at left!')

    def onObstacleRight(self):
        print 'Obstacle at right!'
        self._actions.say('Obstacle at right!')


if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    mainloop = MainLoop(SonarTester)
    mainloop.run()
