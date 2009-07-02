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

# Webots minimal height for robot
webots_min_player_z = 0.32195

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

    def __init__(self):
        Supervisor.__init__(self)
        self.updates = [] # list of objects for which location updates are requested

    def addUpdatee(remote, name):
        class Updater(object):
            def __init__(updater, name):
                updater.name = name
                updater.obj = remote.getFromDef(name)
                updater.trans = updater.obj.getField('translation')
                updater.rot = updater.obj.getField('rotation')
        remote.updates.append(Updater(name))

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

    def on_request_location_update(self, name):
        """ start continueous location updates, once per round - no lost information. will give updates
        to the player with name 'name' """
        if name not in self.updates:
            self.addUpdatee(name)
        
    def on_request_location_update_stop(self, name):
        if name in self.updates:
            del self.updates[name]

    def on_player_name(self, name):
        self._on_object('player', name)

    def on_ball_name(self, name):
        self._on_object('ball', name)

    def _on_object(self, attr_name, name):
        obj = self.getFromDef(name)
        setattr(self, attr_name, obj)
        trans_attr_name = '%s_trans' % attr_name
        rot_attr_name = '%s_rot' % attr_name
        setattr(self, trans_attr_name, obj.getField('translation'))
        setattr(self, rot_attr_name, obj.getField('rotation'))
        print "REMOTE CONTROL: %s = %s" % (attr_name, name)
 
    def on_ball(self, x, y, z):
        """ ball position change in burst coordinates """
        # TODO - we assume yellow gate is at 0,0,0
        x, y, z = world_to_webots_yellow_webots_minus(float(x), float(y), float(z))
        self.ball_trans.setSFVec3f([x, y, z])

    def on_ballw(self, x, y, z):
        """ ball position change in webots coordinates """
        x, y, z = float(x), float(y), float(z)
        self.ball_trans.setSFVec3f([x, y, z])

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
        #print dir(self.player_rot)
        print self.player_rot.getSFRotation()
        print help(self.player_rot.setSFRotation)
        self.player_rot.setSFRotation([x, y, z, angle])

    def on_rotblue(self):
        """ rotate to the blue gate """
        self.player_rot.setSFRotation([0., 1., 0., pi/2])

    def on_rotyellow(self):
        """ rotate to the blue gate """
        self.player_rot.setSFRotation([0., 1., 0., -pi/2])

    def label(self, s):
        self.setLabel(0, s, 0.05,0.01,0.08,0xff0000,0.0)

    def send(self, s):
        self.sock.trySend(s)

    def run(self):
        self.on_player_name('RED_GOAL_KEEPER') # burst.wbt compatible
        self.on_ball_name('BALL') # burst.wbt compatible

        self.sock = sock = NonBlockingListeningSocket(PORT)
        # Main loop
        while True:
            for s, l in sock.readLines():
                self.onCommand(l)
            if self.step(BASIC_TIME_STEP) == -1: break
            for update in self.updates:
                self.send('%r %r' % (update.trans.getSFVec3f(), update.rot.getSFRotation()))
        # Enter here exit cleanup code

if __name__ == '__main__':
    controller = RemoteControl()
    controller.run()

