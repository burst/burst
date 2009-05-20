#!/usr/bin/python
from twisted.internet import gtk2reactor

try:
    gtk2reactor.install()
except:
    pass

from twisted.internet import reactor, task
from twisted.internet.threads import deferToThread

import gtk, gobject, cairo, goocanvas

from math import sin, cos

# add path to burst lib
import os
import sys
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi
from burst_util import cached

REAL_AREA_LENGTH = 7400.0
REAL_AREA_WIDTH = 5400.0
SCREEN_WIDTH = 600.0
SCREEN_HEIGHT = REAL_AREA_WIDTH / REAL_AREA_LENGTH * SCREEN_WIDTH
F = float(SCREEN_HEIGHT) / REAL_AREA_WIDTH
print "F = %s" % F
# Some constants, all sizes in millimemters
BALL_DIAMETER = 90 * F
AREA_LENGTH   = REAL_AREA_LENGTH * F # this is with the field with the out of bounds boundary
AREA_WIDTH    = REAL_AREA_WIDTH * F
# Post == Goal Post, a pole being one side of the game goal.
DIST_BETWEEN_POSTS = 1400 * F
POST_DIAMETER = 100 * F

home = os.environ['HOME']

@cached('%s/.naovision.vision_names.pickle' % home)
def getVisionDataNames(con):
    names = [x for x in con.ALMemory.getDataListName() if x[0] == '/']
    return names

# gooCanvas helpers
def make_circle(root, r, color, **kw):
    return goocanvas.Ellipse(parent = root,
    center_x = 0, center_y = 0, radius_x = r,
    radius_y = r, fill_color = color, **kw)

def make_rect(root, side, color, **kw):
    return goocanvas.Rect(parent = root,
    x = 0, y = 0, width = side, height = side,
    fill_color = color, **kw)

DT_VISION_QUERY=1.0

class Main(object):

    def __init__(self, con):
        self.con = con
        self.names = getVisionDataNames(self.con)
        self._already_notified = False

        self.createFieldAndObjects()
        self.w = w = gtk.Window()
        c = gtk.HBox()
        self.image = gtk.Image()
        w.add(c)
        c.add(self.image)
        c.add(self.field)
        #w.resize(600, 400)
        w.show_all()
        w.connect("destroy", gtk.main_quit)
        self.updater = task.LoopingCall(self.getVision)
        self.updater.start(DT_VISION_QUERY)

    def createFieldAndObjects(self):
        self.field = goocanvas.Canvas()
        self.field.set_size_request(600, 400)
        self.field.set_bounds(0, 0, AREA_LENGTH, AREA_WIDTH)
        root = self.field.get_root_item()
        self.ball = make_circle(root, BALL_DIAMETER/2, 'orange')
        self.my_ball = make_circle(root, BALL_DIAMETER/2, 'red')
        self.vision_ball = make_circle(root, BALL_DIAMETER/2, 'green')
        for attr, color in [('bglp', 'blue'), ('bgrp', 'blue'),
            ('yglp', 'yellow'), ('ygrp', 'yellow')]:
            setattr(self, attr, make_rect(root, POST_DIAMETER, color))

    def notifyUserManModuleIsntLoaded(self):
        if not self._already_notified:
            print ">>>> man module isn't loaded <<<<"
            self._already_notified = True

    def getVision(self):
        """ TODO: callback from twisted
        """
        self.con.ALMemory.getListData(self.names).addCallback(self._onListData)

    def _onListData(self, list_data):
        new_data = dict(zip(self.names, list_data))
        def get(part, attr):
            return new_data['/BURST/Vision/%s/%s/' % (part, attr)]
        def get_many(part, attrs):
            try:
                return [new_data['/BURST/Vision/%s/%s' % (part, attr)] for attr in attrs]
            except:
                print "breakpoint"
                import pdb; pdb.set_trace()
        # centerX, centerY - ball position in image, not very interesting.
        for propname, value in zip(['center-x', 'center-y'],
            get_many('Ball', ['centerX', 'centerY'])):
            if value == 'None':
                self.notifyUserManModuleIsntLoaded()
                return
            else:
                self.vision_ball.set_property(propname, value)

        ball_bearing, ball_dist = get_many('Ball', ['bearing', 'dist'])
        # ball dist is in cm, need to multiply by 10 to get mm
        if ball_dist > 0.0:
            ball_dist = ball_dist * 10 * F
            x0, y0 = AREA_WIDTH / 2, 0
            x, y = x0 + ball_dist * sin(ball_bearing), y0 + ball_dist * cos(ball_bearing)
            print x, y
            self.ball.set_property('center-x', x)
            self.ball.set_property('center-y', y)
        for post in ['BGRP', 'BGLP', 'YGLP', 'YGRP']:
            obj = getattr(self, post.lower())
            bearing_deg, distance = get_many(post, ['BearingDeg', 'Distance'])
            x, y  = get_many(post, ['CenterX', 'CenterY'])
            if distance > 0.0:
                obj.set_property('x', x)
                obj.set_property('y', y)
        # compute bearing my self, then set myball to that position

if __name__ == '__main__':
    main = Main(pynaoqi.getDefaultConnection(with_twisted=True))
    reactor.run()

