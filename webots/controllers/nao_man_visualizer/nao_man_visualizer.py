# File:
# Date:
# Description:
# Author:
# Modifications:

import cPickle
#from math import sin, cos, atan2
from math import atan2

from numpy import *

from controller import Supervisor

import burst

# This number should correspond to the basicTimeStep
# in the wbt file
BASIC_TIME_STEP = 40

#from util import opendebugsocket
#opendebugsocket()


class MyController (Supervisor):

    silent = True

    def callman(self, s):
        return getattr(self.man, s)()

    def nao(self, s):
        # safety
        compile(s, 'test', 'eval') # will raise an error, but won't possibly kill the nao
        return self.man.pyEval(s)

    def naoexec(self, s):
        # safety
        compile(s, 'test', 'single') # will raise an error, but won't possibly kill the nao
        return self.man.pyExec(s)

    def run(self):
        MS_INIT_WAIT = 3000
        secs = int(MS_INIT_WAIT / 1000.0)
        self.man = None
        init_worked = False
        num_connect_attempts = 0
        while not self.man:
            print "waiting %s seconds" % (secs)
            for i in xrange(int(MS_INIT_WAIT/BASIC_TIME_STEP)+1):
                if self.step(BASIC_TIME_STEP) == -1:
                    return
            num_connect_attempts += 1
            print "connection attempt %s" % num_connect_attempts
            if not init_worked:
                try:
                    print "burst.init called"
                    burst.init()
                except Exception, e:
                    print e
                else:
                    init_worked = True
                    print "connected to soap"
            if init_worked:
                try:
                    self.man = burst.ALProxy('Man')
                except Exception, e:
                    print e


        print "connected"

        # Get some references - ball, oball (visualization), player
        player = self.getFromDef('RED_GOAL_KEEPER')
        player_trans = player.getField('translation')
        player_rot = player.getField('rotation')
        ball = self.getFromDef('BALL')
        ball_trans = ball.getField('translation')
        ball_trans.setSFVec3f([0.0,0.0,1.0]) # doesn't work for some reason
        root = self.getRoot()
        children = root.getField('children')
        children.importMFNode(-1,'other_ball.wbt') # the file needs to be in the specific supervisor directory
        oball = self.getFromDef('OTHER_BALL')
        oball_trans = oball.getField('translation')

        #self.naoexec('fd=open("/tmp/bla","w+");fd.write(str(brain.ball.lastVisionBearing));fd.close();print "ok"')
        #ang = float(open('/tmp/bla').read().strip())

        old_v = zeros(4)

        # Main loop
        while True:
            #self.label(repr(ball_trans.getSFVec3f()))
            ang = float(self.callman('cachedBallBearing'))
            p_v = player_trans.getSFVec3f()
            b_v = ball_trans.getSFVec3f()
            true_ang = atan2(b_v[2] - p_v[2], p_v[0] - b_v[0])
            p_quat = player_rot.getSFRotation()
            p_heading = p_quat[3] # TODO
            v = array([ang, p_heading, ang+p_heading, true_ang])
            if linalg.norm(old_v - v) > 1e-3:
                if not self.silent:
                    print '%0.3f %0.3f %0.3f %0.3f (%0.3f %0.3f %0.3f %0.3f)' % (
                        v[0], v[1], v[2], v[3], p_quat[0], p_quat[1], p_quat[2], p_quat[3])
                old_v = v
            #ang += p_heading
            oball_trans.setSFVec3f([p_v[0] - 1.0 * cos(ang), p_v[1] + 1, p_v[2] + 1.0 * sin(ang)])

            if self.step(BASIC_TIME_STEP) == -1: break

        # Enter here exit cleanup code

    def label(self, s):
        self.setLabel(0, s, 0.05,0.01,0.08,0xff0000,0.0)

if __name__ == '__main__':
    controller = MyController()
    controller.run()

