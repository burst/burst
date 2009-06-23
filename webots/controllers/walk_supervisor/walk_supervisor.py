import cPickle
#from math import sin, cos, atan2
from math import *

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

        f = open('out_params.txt','w')
        # Get some references - ball, oball (visualization), player
        player = self.getFromDef('PLAYER_1')
        player_trans = player.getField('translation')
        player_rot = player.getField('rotation')
        player_trans.setSFVec3f([0, 0.325, 0]) # doesn't work for some reason
        player_new_pos = array(player_trans.getSFVec3f())

        counter = 0
        run_num= 0
        # Main loop
        while True:
            counter += 1
            if counter % 100 == 0:
                player_old_pos = player_new_pos
                player_new_pos = array(player_trans.getSFVec3f())
                x_pos = array(player_trans.getSFVec3f())[0]
                y_pos = array(player_trans.getSFVec3f())[2]
                rotation = (player_rot.getSFRotation()[3])*180/math.pi
                rotation += 90
                if rotation<0:
                    rotation += 360
                print math.floor(run_num/3)+1, ' - [' , x_pos, ',', y_pos, ',', rotation, ']'
            if self.step(BASIC_TIME_STEP) == -1: break
        # Enter here exit cleanup code

    def label(self, s):
        self.setLabel(0, s, 0.05,0.01,0.08,0xff0000,0.0)

if __name__ == '__main__':
    controller = MyController()
    controller.run()

