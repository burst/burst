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
        player = self.getFromDef('RED_GOAL_KEEPER')
        player_trans = player.getField('translation')
        player_rot = player.getField('rotation')
        ball = self.getFromDef('BALL')
        ball_trans = ball.getField('translation')
        ball_trans.setSFVec3f([0.0, 0.0, 1.0])
        
        # Main loop
        while True:
            if self.step(BASIC_TIME_STEP) == -1: break
        
        # Enter here exit cleanup code

    def label(self, s):
        self.setLabel(0, s, 0.05,0.01,0.08,0xff0000,0.0)

if __name__ == '__main__':
    controller = MyController()
    controller.run()

