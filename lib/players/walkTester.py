#!/usr/bin/python

# DON'T PUT ANYTHING BEFORE THIS LINE
import player_init

from burst.player import Player
from burst_consts import *
import burst.moves.walks as walks
import burst.moves.poses as poses

import time

class WalkTester(Player):
    
    def onStart(self):
        self.movesList = [
#                     ('Walk straight - Asaf''s version (Stable walk)',
#                      lambda: self._actions.executeMoveRadians(poses.STABLE_WALK_INITIAL_POSE).onDone(
#                      lambda: self._actions.changeLocationRelative(50.0, 0.0, 0.0, walk=walks.STABLE_WALK))),
                      
                     ('Walk straight',
                      lambda: self._actions.executeMoveRadians(poses.STRAIGHT_WALK_INITIAL_POSE).onDone(
                      lambda: self._actions.changeLocationRelative(50.0, 0.0, 0.0, walk=walks.STRAIGHT_WALK))),
                      
#                     ('Walk sideways',
#                      lambda: self._actions.changeLocationRelativeSideways(0.0, 20.0, walk=walks.SIDESTEP_WALK)),

#                     ('Turn 90 degrees (Straight walk params)',
#                      lambda: self._actions.turn(1.57, walk=walks.STRAIGHT_WALK)),

#                     ('Sit',
#                     lambda: self._actions.sitPoseAndRelax())
                     ]
        
        self._actions.initPoseAndStiffness().onDone(self.doNextMove)
        
    def doNextMove(self):
        if len(self.movesList) > 0:
            self.testMove(self.movesList.pop(0))
        else:
            self.onTestDone()
    
    def testMove(self, (moveName, moveFunc)):
        print "%s Started!" % moveName
        self.moveStartTime = time.time()
        moveFunc().onDone(self.onMoveDone)
        
    def onMoveDone(self):
        print "Took approximately %f" % (time.time() - self.moveStartTime)
        self.doNextMove()
    
    def onTestDone(self):
        self._eventmanager.quit()

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(WalkTester).run()
