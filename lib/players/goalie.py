#!/usr/bin/python
import os
in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

from burst.player import Player
from burst.events import *
from burst.consts import *
import burst.moves as moves
from math import cos, sin
import time

GOAL_BORDER = 57
ERROR_IN_LENGTH = 0

class goalie(Player):
    
    
#    def onStop(self):
#        super(Goalie, self).onStop()

    def onStart(self):
        self.kp = None
            
        self._eventmanager.register(EVENT_CHANGE_LOCATION_DONE, self.onChangeLocationDone)        
        self._actions.initPoseAndStiffness()
        
        #self._eventmanager.register(EVENT_BALL_IN_FRAME,
        #    lambda target=self._world.ball: self._actions.executeTracking(target)
        #)
        #self._eventmanager.register(EVENT_BALL_IN_FRAME, self.trackBall)
        
        #self.doMoveHead(self._world.ball.bearing, -self._world.ball.elevation)
        #self._actions.executeLeapLeft()
        #self.walkStartTime = time.time()
        #self.test()
        
        
        
        
        self.watchIncomingBall()
        
        
    def watchIncomingBall(self):
        self._eventmanager.register(EVENT_BALL_BODY_INTERSECT_UPDATE, self.leap)
        
    def leap(self):
        self._eventmanager.unregister(EVENT_BALL_BODY_INTERSECT_UPDATE)
        print self._world.ball.body_isect
        if self._world.ball.body_isect < 0 and self._world.ball.body_isect > -(GOAL_BORDER + ERROR_IN_LENGTH):
            self._actions.executeLeapRight()
            self._eventmanager.setTimeoutEventParams(3.0, oneshot=True, cb=self.gettingUpRight)
        else:
            self.watchIncomingBall()
        
        
    def gettingUpRight(self):
        self._actions.executeToBellyFromLeapRight()
        self._actions.executeGettingUpBelly().onDone(self.watchIncomingBall)
    
    def trackBall(self):
        self._actions.executeTracking(self._world.ball)
    
    #def doMoveHead(self, deltaHeadYaw, deltaHeadPitch):
    #    self._actions.changeHeadAnglesRelative(deltaHeadYaw, deltaHeadPitch)
   
    def test(self):
        self._actions.changeLocationRelative(100.0)
#        self._actions.executeSyncMove(moves.GREAT_KICK_RIGHT)
#        self._actions.executeSyncMove(moves.GREAT_KICK_LEFT)
#        self._actions.sitPoseAndRelax()
#        self._eventmanager.quit()
    
    def onChangeLocationDone(self):
        self.walkEndTime = time.time()
        print "Walk Done! - tool approximately %f" % (self.walkEndTime - self.walkStartTime)
        #self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(goalie).run()

