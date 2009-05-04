# File:         
# Date:         
# Description:  
# Author:       
# Modifications:

import cPickle
#from math import sin, cos, atan2
from math import atan2

from numpy import *
from numpy.linalg import *

from controller import Supervisor

# This number should correspond to the basicTimeStep
# in the wbt file
BASIC_TIME_STEP = 40

#from util import opendebugsocket
#opendebugsocket()


class MyController (Supervisor):

    def run(self):
    
        # Get some references - ball, oball (visualization), player
        player = self.getFromDef('PLAYER_1')
        player_trans = player.getField('translation')
        player_rot = player.getField('rotation')
        player_trans.setSFVec3f([0.0,0.0,0.0]) # doesn't work for some reason
        
        old_v = zeros(4)

        counter = 0
        # Main loop
        while True:
            #self.label(repr(ball_trans.getSFVec3f()))
            counter += 1
            dist = norm(array(player_trans.getSFVec3f()))
            print "distance from start = %s" % dist
            if counter % 100 == 0:
                player_trans.setSFVec3f([0.0, 0.0, 0.0])
            if self.step(BASIC_TIME_STEP) == -1: break
        
        # Enter here exit cleanup code

    def label(self, s):
        self.setLabel(0, s, 0.05,0.01,0.08,0xff0000,0.0)

if __name__ == '__main__':
    controller = MyController()
    controller.run()

