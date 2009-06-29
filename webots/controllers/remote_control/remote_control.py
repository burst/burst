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

def matmult(m, v):
    return ((m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2] + m[0][3] * v[3]),
            (m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2] + m[1][3] * v[3]),
            (m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2] + m[2][3] * v[3]),
            (m[3][0] * v[0] + m[3][1] * v[1] + m[3][2] * v[2] + m[3][3] * v[3]))

# Some magic consts - just make sure they correspond to the right points,
# you can change the location manually in webots and see if it works,
# or read the VRML Tree and figure out the final transform.
webots_goal_dist_from_center = 3.11 * 1.07 #3.3277
burst_field_width = 605.0 # cm
k = webots_goal_dist_from_center / (burst_field_width / 2)

m_yellow_webots_minus = [
    [-k, 0, 0, 0],
    [0, 0, k, 0],
    [0, k, 0, 0],
    [0, 0, 0, k],
]

def world_to_webots_yellow_webots_minus(x, y, z):
    """ Input: centimeters, world coordinates (our goal, here
    assumed to be blue, is 0,0,0, and enemies is 605,0,0, right
    handed coordinate system)
    
    This converts world coordinates to webots coordinates, assuming
    that the yellow goal in webots is in the negative X direction, and
    that we are playing the blue team, so that corresponds to:
    webots -3.1 0 0 == burst 6.2 0 0
    """
    return matmult(m_yellow_webots_minus, (x, y, z, 1))[:3]

class RemoteControl (Supervisor):

    def onCommand(self, line):
        parts = line.split()
        cmd, params = parts[0], parts[1:]
        attr_name = 'on_%s' % (cmd.lower())
        if not hasattr(self, attr_name):
            print "RemoteControl: No such command %r; line: %r" % (cmd, line)
            return
        method = getattr(self, attr_name)
        method_args = method.im_func.func_code.co_argcount - 1
        if method_args != len(params):
            msg = 'Not enough arguments' if len(params) < method_args else (
                'Too many args')
            print "RemoteControl: %s, given %s, needed %s" % (msg, len(params), method_args)
            return
        try:
            method(*params)
        except Exception, e:
            print "RemoteControl: Error running %s: %s" % (cmd, e)

    def on_player(self, name):
        self.player = player = self.getFromDef(name)
        self.player_trans = player.getField('translation')
        self.player_rot = player.getField('rotation')
        print "REMOTE CONTROL: Player = %s" % name
 
    def on_pos(self, x, y, z):
        """ position change in burst coordinates """
        # TODO - we assume yellow gate is at 0,0,0
        x, y, z = world_to_webots_yellow_webots_minus(float(x), float(y), float(z))
        self.player_trans.setSFVec3f([x, y, z])

    def on_posw(self, x, y, z):
        """ position change in webots coordinates """
        x, y, z = float(x), float(y), float(z)
        self.player_trans.setSFVec3f([x, y, z])

    def on_rot(self, x, y, z, angle):
        x, y, z, angle = map(float, [x, y, z, angle])

    def label(self, s):
        self.setLabel(0, s, 0.05,0.01,0.08,0xff0000,0.0)

    def run(self):
        self.on_player('RED_GOAL_KEEPER') # burst.wbt compatible

        sock = NonBlockingListeningSocket(PORT)
        # Main loop
        while True:
            for s, l in sock.readLines():
                self.onCommand(l)
            if self.step(BASIC_TIME_STEP) == -1: break
        # Enter here exit cleanup code

if __name__ == '__main__':
    controller = RemoteControl()
    controller.run()

