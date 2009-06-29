"""
Supervisor that does the following:

opens a port.
starts the loop
checks on port, if gets something does the command.
otherwise sleeps.

commands:
position change
rotation change

protocol:
ascii, line based, first word is the command, rest are command specific.

position command:
POS <X> <Y> <Z>
rotation command:
ROT <X> <Y> <Z> <ANGLE>
"""

from debugsocket import NonBlockingListeningSocket
PORT=13434

import cPickle
#from math import sin, cos, atan2
from math import *

from numpy import *
from numpy.linalg import *

from controller import Supervisor

# This number should correspond to the basicTimeStep
# in the wbt file
BASIC_TIME_STEP = 40

class MyController (Supervisor):

    def onCommand(self, line):
        parts = line.split()
        cmd, params = parts[0], parts[1:]
        getattr(self, 'on_%s' % (cmd.lower()))(*params)

    def on_player(self, name):
        self.player = player = self.getFromDef(name)
        self.player_trans = player.getField('translation')
        self.player_rot = player.getField('rotation')
        print "REMOTE CONTROL: Player = %s" % name
 
    def on_pos(self, x, y, z):
        x, y, z = float(x), float(y), float(z)
        player_trans.setSFVec3f([0, 0.325, 0]) # doesn't work for some reason

    def on_rot(self, x, y, z, angle):
        x, y, z, angle = map(float, [x, y, z, angle])

    def label(self, s):
        self.setLabel(0, s, 0.05,0.01,0.08,0xff0000,0.0)

    def run(self):
        self.on_player('RED_GOAL_KEEPER') # burst.wbt compatible
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

if __name__ == '__main__':
    controller = MyController()
    controller.run()

