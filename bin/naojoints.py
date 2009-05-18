#!/usr/bin/python
from time import time
from math import pi

from twisted.internet import gtk2reactor

try:
    gtk2reactor.install()
except:
    pass

from twisted.internet import reactor, task
from twisted.internet.defer import succeed
from twisted.internet.threads import deferToThread

import gtk, gobject, cairo, goocanvas

# add path to burst lib
import os
import sys
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi
from burst_util import cached, cached_deferred, Deferred

import burst.moves as moves

DT_CHECK_FOR_NEW_ANGLES   = 0.5 # seconds between socket calls
DT_CHECK_FOR_NEW_INERTIAL = 0.5

def toggle(initial=False):
    """ make a function into a toggle - this lets that function access a variable
    on it's own function object called state, which starts out at initial
    """
    def wrapgen(f):
        f.state = initial
        def wrapper(*args, **kw):
            ret = f(*args, **kw)
            f.state = not f.state
            return ret
    return wrapgen

red = gtk.gdk.rgb_get_colormap().alloc_color('red')
green = gtk.gdk.rgb_get_colormap().alloc_color('green')

@cached_deferred('%s/.burst_joint_data.pickle' % os.environ['HOME'])
def getJointData(con):

    results = {}
    collecting = Deferred()

    def collect_callback(joint_names):
        print "Collecting Joint Limits (need %s):" % len(joint_names),
        def store_one(jointname, result):
            results[jointname] = result
            print "%s," % len(results),
            if len(results) == len(joint_names):
                # finally!
                print "Joint Limits Done"
                collecting.callback((joint_names, results))
        for joint_name in joint_names:
            con.ALMotion.getJointLimits(joint_name).addCallback(
                lambda result, joint_name=joint_name: store_one(joint_name, result))

    # NOTE - not using con.ALMotion.initDeferred, not sure it can be called multiple times, need
    # to minimize the usage of that deferred.
    con.ALMotion.getBodyJointNames().addCallback(collect_callback)

    return collecting

localization_vars = [
 '/BURST/Loc/Ball/XEst',
 '/BURST/Loc/Ball/XUncert',
 '/BURST/Loc/Ball/XVelocityEst',
 '/BURST/Loc/Ball/XVelocityUncert',
 '/BURST/Loc/Ball/YEst',
 '/BURST/Loc/Ball/YUncert',
 '/BURST/Loc/Ball/YVelocityEst',
 '/BURST/Loc/Ball/YVelocityUncert',
 '/BURST/Loc/Self/HEst',
 '/BURST/Loc/Self/HEstDeg',
 '/BURST/Loc/Self/HUncert',
 '/BURST/Loc/Self/HUncertDeg',
 '/BURST/Loc/Self/LastOdoDeltaF',
 '/BURST/Loc/Self/LastOdoDeltaL',
 '/BURST/Loc/Self/LastOdoDeltaR',
 '/BURST/Loc/Self/XEst',
 '/BURST/Loc/Self/XUncert',
 '/BURST/Loc/Self/YEst',
 '/BURST/Loc/Self/YUncert',
]

# All units in centimeters
FIELD_OUTER_LENGTH = 740
FIELD_OUTER_WIDTH = 540
FIELD_LENGTH = 605
FIELD_WIDTH = 405

# 0,0 is bottom left of outer field (so all values are positive).
# x points towards yellow goal, y is positive for up.
GOAL_LEN = 140.0
OUTER_X_BUFFER = 67.5
BGRP_X = OUTER_X_BUFFER
BGRP_Y = FIELD_OUTER_WIDTH / 2.0 + GOAL_LEN / 2.0
BGLP_X = OUTER_X_BUFFER
BGLP_Y = FIELD_OUTER_WIDTH / 2.0 - GOAL_LEN / 2.0
YGRP_X = OUTER_X_BUFFER + FIELD_LENGTH
YGRP_Y = FIELD_OUTER_WIDTH / 2.0 + GOAL_LEN / 2.0
YGLP_X = OUTER_X_BUFFER + FIELD_LENGTH
YGLP_Y = FIELD_OUTER_WIDTH / 2.0 - GOAL_LEN / 2.0

fol = FIELD_OUTER_LENGTH
fow = FIELD_OUTER_WIDTH
fl = FIELD_LENGTH
fw = FIELD_WIDTH

LOC_SCREEN_X_SIZE = 740.0
LOC_SCREEN_Y_SIZE = 540.0

def maxmin():
    val = yield()
    themin = val
    themax = val
    while True:
        val = yield(themin, themax)
        themin, themax = min(themin, val), max(themax, val)

class MyCircle(object):
    """ Normalize coordinates
    """
    _screen_x, _screen_y = LOC_SCREEN_X_SIZE, LOC_SCREEN_Y_SIZE
    _xf, _yf = _screen_x / fol, _screen_y / fow # 1/cm
    print "XF = %s, YF = %s" % (_xf, _yf)
    # The position of the center on screen point, in local (field, set_x/set_y) coordinates
    _cx, _cy = 0.5 * fol, 0.5 * fow
    _cx_screen, _cy_screen = _screen_x / 2, _screen_y / 2

    @classmethod
    def fromCircle(cls, ex):
        el = ex._ellipse
        c = MyCircle(parent = el.get_parent(),
            center_x = ex._x,
            center_y = ex._y,
            radius = ex._radius,
            fill_color = ex._fill_color)
        return c

    def __init__(self, parent, center_x, center_y, radius,
        fill_color):
        _cx, _cy, _xf, _yf = self._cx, self._cy, self._xf, self._yf
        self._ellipse = goocanvas.Ellipse(parent = parent,
            center_x = 0.0, center_y = 0.0,
            radius_x = radius * _xf, radius_y = radius * _yf,
            fill_color = fill_color)
        self._radius = radius
        self._fill_color = fill_color
        self._x = center_x
        self._y = center_y
        self.set_x(center_x)
        self.set_y(center_y)
        self.maxmin_x = maxmin()
        self.maxmin_x.next()
        self.maxmin_y = maxmin()
        self.maxmin_y.next()

    def get_x(self):
        return self._x

    def get_screen_x(self):
        return (self._x - self._cx) * self._xf + self._cx_screen

    def set_x(self, x):
        self._x = x
        if hasattr(self, 'maxmin_x'):
            self.maxmin_x_val = self.maxmin_x.send(x)
        self._ellipse.set_property('center-x', self.get_screen_x())

    def get_y(self):
        return self._y

    def get_screen_y(self):
        return (self._y - self._cy) * self._yf + self._cy_screen
    
    def set_y(self, y):
        self._y = y
        if hasattr(self, 'maxmin_y'):
            self.maxmin_y_val = self.maxmin_y.send(y)
        self._ellipse.set_property('center-y', self.get_screen_y())

    x = property(get_x, set_x)
    y = property(get_y, set_y)

class Localization(object):

    def __init__(self, con):
        self.con = con
        self.w = w =gtk.Window()
        w.set_title('localization - %s' % con.host)
        c = gtk.VBox()
        w.add(c)
        self.field = goocanvas.Canvas()
        self.field.set_size_request(LOC_SCREEN_X_SIZE, LOC_SCREEN_Y_SIZE)
        c.add(self.field)
        self.objects = []
        self.snapshots = []
        self.root = root = self.field.get_root_item()
        for color, x, y in [
            ('blue', BGLP_X, BGLP_Y),
            ('blue', BGRP_X, BGRP_Y),
            ('yellow', YGLP_X, YGLP_Y),
            ('yellow', YGRP_X, YGRP_Y),
            ('orange', 0, 0),
            ('black', FIELD_OUTER_LENGTH/4, 0)]:
            obj = MyCircle(parent = root,
                center_x = x, center_y = y, radius = 5,
                fill_color = color)
            self.objects.append(obj)
        self.robot = self.objects[-1]
        self.ball  = self.objects[-2]
        snapshot = gtk.Button('snapshot')
        snapshot.connect('clicked', self.onSnapshot)
        c.pack_start(snapshot, False, False, 0)

        self._pairs = []
        self.localized = {}
        for v in localization_vars:
            _, __, ___, obj, key = v.split('/')
            if obj not in self.localized:
                self.localized[obj] = {}
            if key not in self.localized[obj]:
                self.localized[obj][key] = 0.0
            self._pairs.append((obj, key))

        w.show_all()
        self.vars = localization_vars
        con.ALMemory.initDeferred.addCallback(self.installUpdater)

    def installUpdater(self, _):
        self.updater = task.LoopingCall(self.getVariables)
        self.updater.start(DT_CHECK_FOR_NEW_INERTIAL)

    def getVariables(self):
        self.con.ALMemory.getListData(self.vars).addCallback(self.updateField)

    def onSnapshot(self, name=None):
        # TODO - different color, filters
        self.snapshots.append([])
        for i in xrange(4,6):
            self.snapshots[-1].append(MyCircle.fromCircle(self.objects[i]))

    def updateField(self, vals):
        """ localization values are in centimeters """
        for (obj, key), v in zip(self._pairs, vals):
            self.localized[obj][key] = v
        read = (self.localized['Ball']['XEst'],
                self.localized['Ball']['YEst'],
                self.localized['Self']['XEst'],
                self.localized['Self']['YEst'])
        print "read:   %3.3f %3.3f %3.3f %3.3f" % read
        self.ball.x, self.ball.y, self.robot.x, self.robot.y = read
        print 'screen: %3.3f %3.3f %3.3f %3.3f' % (self.ball.get_screen_x(), self.ball.get_screen_y(), self.robot.get_screen_x(), self.robot.get_screen_y())
        print "ball:   %s, %s" % (self.ball.maxmin_x_val, self.ball.maxmin_y_val)


class Inertial(object):

    def __init__(self, con):
        self.con = con
        self.w = w =gtk.Window()
        c = gtk.HBox()
        w.add(c)
        self.l = []
        self.values = [(k, 'Device/SubDeviceList/InertialSensor/%s/Sensor/Value' % k) for
            k in ['AccX', 'AccY', 'AccZ', 'AngleX', 'AngleY', 'GyrX', 'GyrY']]
        self.vars = [v for k,v in self.values]
        for k, v in self.values:
            self.l.append(gtk.Label())
            c.add(self.l[-1])

        w.show_all()
        self.updater = task.LoopingCall(self.getInertial)
        self.updater.start(DT_CHECK_FOR_NEW_INERTIAL)

    def getInertial(self):
        self.con.ALMemory.getListData(self.vars).addCallback(self.updateLists)

    def updateLists(self, vals):
        for l, new_val in zip(self.l, vals):
            l.set_label('%3.3f' % new_val)

class ToggleButton(object):
    
    def __init__(self, button, widgets):
        self._button = button
        self._state = False
        self._widgets = widgets
        self._button.connect("clicked", self.onButtonPress)
        self._colors = {False:red, True:green}

    def onButtonPress(self, _):
        if self._state:
            for w in self._widgets:
                w.show_all()
        else:
            for w in self._widgets:
                w.hide_all()
        self._state = not self._state
        self._button.modify_fg(gtk.STATE_INSENSITIVE, self._colors[self._state])

def color(i):
    if i < 2: return 'green'
    if i < 8: return 'red'
    if i < 14: return 'blue'
    if i < 20: return 'purple'
    return 'red'

class Scale(object):
    """ A single scale for one joint. Has multiple widgets, delegates actually adding
    them to a table to the caller. Store all the widgets in self.col in the order
    to add to the table.
    """

    MIN_TIME_BETWEEN_CHANGES = 0.1 # throtelling - seems I make nao's stuck? naoqi problem?
    NUM_ROWS = 4
    both = gtk.FILL | gtk.EXPAND
    ROW_OPTIONS = [(0, 0), (0, 0), (0, 0), (both, both)]
    assert(len(ROW_OPTIONS) == NUM_ROWS)

    def __init__(self, i, name, min_val, max_val, init_pos):
        self.last_sent_value = min_val
        self.last_sent_time = start_time
        self.name = name
        range_val = max_val - min_val
        step = range_val / 1000.0
        page_step = range_val / 10.0
        page_size = page_step
        adj = gtk.Adjustment(init_pos, min_val, max_val, step, page_step, page_size)
        self.set_scale = gtk.VScale(adj)
        self.set_scale.connect("change-value", self.onChanged)
        adj = gtk.Adjustment(min_val, min_val, max_val, step, page_step, page_size)
        self.state_scale = gtk.VScale(adj)
        self.toplabel = gtk.Label()
        self.toplabel.set_markup('<span foreground="%s">%s</span>' % (color(i), i))
        self.label = gtk.Label(self.name)
        self.label.set_property('angle', 90)
        self.count_label = gtk.Label('0')
        self.lowbox = gtk.HBox()
        self.lowbox.add(self.set_scale)
        self.lowbox.add(self.state_scale)
        # This list is the order of the elements in the table
        self.col = [self.toplabel, self.count_label, self.label, self.lowbox]
        assert(len(self.col) == self.NUM_ROWS)
        #self.box.pack_start(self.toplabel, False, False, 0)

        self._last = [] # list of all the deferreds for our gotoAngleWithSpeed requests
        self._waiting_callbacks = 0

    def onChanged(self, w, scroll_type, val):
        cur = time()
        if cur - self.last_sent_time < Scale.MIN_TIME_BETWEEN_CHANGES:
            return
        self.last_sent_value = cur
        s = self.set_scale
        # TODO: throtlling?
        # name, value, speed percent [0-100], interpolation (1 = smooth)

        if len(self._last) > 0 and self._last[-1].called:
            #print "zeroing deferred list"
            self.count_label.set_label('0')
            del self._last[:]
            self._waiting_callbacks = 0

        def gotoAngle(ind, val):
            #print "joint %s, ind %s, value %s %s" % (
            #            self.name, ind, s.get_value(), val)
            if ind == self._waiting_callbacks:
                d = con.ALMotion.gotoAngleWithSpeed(self.name, val, 50, 1)
            else:
                #print "not moving, %s != %s" % (ind, self._waiting_callbacks)
                d = succeed(0)
            self._last.append(d)
            return d

        if len(self._last) == 0:
            # first call, bery simple!
            self._last.append(gotoAngle(self._waiting_callbacks, val))
        else:
            self._waiting_callbacks += 1
            ind = self._waiting_callbacks
            self.count_label.set_label('%s' % len(self._last))
            self._last[-1].addCallback(lambda _,
                    ind=ind, val=val: gotoAngle(ind, val))

class Main(object):

    def __init__(self):
        global start_time
        global con
        start_time = time()
              
        self.scales = scales = {}
        self.con = pynaoqi.getDefaultConnection(with_twisted=True)
        con = self.con
        self.vision = None
        self.inertial = None
        self.localization = None
        self.toggleLocalization(None)

        # Create the joint controlling and displaying slides (called by onJointData)
        def onBodyAngles(cur_angles):
            table = gtk.Table(rows=Scale.NUM_ROWS, columns=len(self.joint_names), homogeneous=False)
            # update visibility toggling lists
            self._joints_widgets.add(table)
            self._all_widgets.add(table)
            c.add(table)
            for i, (joint_name, cur_a) in enumerate(zip(self.joint_names, cur_angles)):
                min_val, max_val, max_change_per_step = self.joint_limits[joint_name]
                s = Scale(i, joint_name, min_val, max_val, cur_a)
                scales[joint_name] = s
                for (row, obj), (xoptions, yoptions) in zip(enumerate(s.col), Scale.ROW_OPTIONS):
                    table.attach(obj, i, i+1, row, row+1, xoptions, yoptions)
                # value-changed is raised also when set_value is called
                # move-scaler - nothing?
            self.updater = task.LoopingCall(self.getAngles)
            self.updater.start(DT_CHECK_FOR_NEW_ANGLES)
            # we added a bunch of widgets, show them (this is async to __init__)
            w.show_all()

        def onJointData(results):
            # called when we have the joint number, we can do this parallel but it's not
            # that time consuming. Besides, joint data is cached, should only happen once on the
            # machine (unless you delete ~/.burst_joint_data.pickle
            self.joint_names, self.joint_limits = results
            self.con.ALMotion.getBodyAngles().addCallback(onBodyAngles)

        # initiate network request that will lead to slides creation.
        # do everything based on a initDeferred, otherwise methods will not be available.
        self.con.ALMotion.initDeferred.addCallback(lambda _: getJointData(self.con).addCallback(onJointData))
        w = gtk.Window()
        w.set_title('naojoints - %s' % self.con.host)
        self.c = c = gtk.VBox()
        w.add(c)

        # Create Many Buttons on Top

        def create_button_strip(data):
            button_box = gtk.HBox()
            buttons = []
            for label, cb in data:
                b = gtk.Button(label)
                if cb:
                    b.connect("clicked", cb)
                button_box.add(b)
                buttons.append(b)
            return button_box, buttons

        top_buttons_data = [
            ('print angles',    self.printAngles),
            ('stiffness on',    self.setStiffnessOn),
            ('stiffness off',   self.setStiffnessOff),
            ('vision',          self.toggleVision),
            ('inertial',        self.toggleInertial),
            ('localization',    self.toggleLocalization),
            ]
        chains = ['Head', 'LLeg', 'LArm', 'RArm', 'RLeg']
        stiffness_off_buttons_data = [
                ('%s OFF' % chain,
                    lambda _, chain=chain: self.con.ALMotion.setChainStiffness(chain, 0.0))
                for chain in chains]
        stiffness_on_buttons_data = [
                ('%s on' % chain,
                    lambda _, chain=chain: self.con.ALMotion.setChainStiffness(chain, 1.0))
                for chain in chains]

        moves_buttons_data = [(move_name, lambda _, move=getattr(moves, move_name):
            self.con.ALMotion.executeMove(move))
                for move_name in moves.NAOJOINTS_EXECUTE_MOVE_MOVES]

        self._walkconfig = [0.05, 0.02, 0.02, 0.35, 0.015, 0.018]

        def updateWalkConfig(_):
            self.con.ALMotion.getWalkConfig().addCallback(self.setWalkConfig)

        self._start_walk_count = 1
        def startWalkTest(result=None):
            print "start walk req %s" % self._start_walk_count
            self._start_walk_count += 1
            self.con.ALMotion.getRemainingFootStepCount().addCallback(startWalkCb)

        def startWalkCb(steps):
            if steps > 0:
                print "remaining footsteps, not calling walk"
            else:
                self.con.ALMotion.walk()

        def doWalk(steps):
            # distance [m], # 20ms cycles per step
            perstep = self._walkconfig[0]
            return self.con.ALMotion.addWalkStraight(steps*perstep, 60).addCallback(
                startWalkTest)

        def doArc(angle):
            # angle [rad], radius [m], # 20ms cycles per step
            return self.con.ALMotion.addWalkArc(angle, 0.5, 60).addCallback(
                startWalkTest)

        def doTurn(angle):
            # angle [rad], # 20ms cycles per step
            return self.con.ALMotion.addTurn(steps, 60).addCallback(
                startWalkTest)

        toggle_buttons_data = [
            ('all', self.onShowAll),
            ('joints only', self.onShowJointsOnly),
            ('stiffness toggle', None),
            ('buttons only', self.onShowButtonsOnly),
        ]
        stiffness_toggle_index = 2

        walk_steps = 4

        walk_buttons_data = [
            ('Walk: get config', updateWalkConfig),
            ('fw %s' % walk_steps, lambda _, steps=walk_steps: doWalk(walk_steps)),
            ('rev %s' % walk_steps, lambda _, steps=-walk_steps: doWalk(-walk_steps)),
            ('rt 45', lambda _, steps=1: doTurn(pi / 4)),
            ('lt 45', lambda _, steps=-1: doTurn(-pi / 4)),
            ('arc right 1', lambda _, steps=1: doArc(1)),
            ('arc left 1', lambda _, steps=-1: doArc(-1)),
        ]

        top_strip, top_buttons       = create_button_strip(top_buttons_data)
        stiffness_off, self.stiffness_off_buttons = (
                                       create_button_strip(stiffness_off_buttons_data))
        stiffness_on, self.stiffness_on_buttons = (
                                       create_button_strip(stiffness_on_buttons_data))
        moves_strip, moves_buttons   = create_button_strip(moves_buttons_data)
        walk_strip, walk_buttons     = create_button_strip(walk_buttons_data)
        toggle_strip, toggle_buttons = create_button_strip(toggle_buttons_data)

        # Python bug? if I don't set the result of ToggleButton to something
        # it is lost to the garbage collector.. very hard to debug, since you just
        # have a missing dictionary, but no actual error..
        self._stiffness_toggle = ToggleButton(button=toggle_buttons[stiffness_toggle_index],
            widgets = (stiffness_on, stiffness_off))

        for button_strip in [top_strip, toggle_strip, stiffness_off, stiffness_on, moves_strip, walk_strip]:
            c.pack_start(button_strip, False, False, 0)
    
        # lists for toggling visibility with appropriate callbacks
        self._buttons_widgets = set([stiffness_off, stiffness_on, moves_strip, walk_strip])
        self._joints_widgets = set([])
        self._all_widgets = self._buttons_widgets.union(self._joints_widgets)

        # Create walk buttons (later need to allow hiding them)
        button_box = gtk.HBox()

        w.resize(700, 400)
        w.show_all()
        w.connect("destroy", self.onDestroy)
    
    def onShowAll(self, _):
        for w in self._all_widgets:
            w.show_all()

    def onShowJointsOnly(self, _):
        for w in self._joints_widgets:
            w.show_all()
        for w in self._buttons_widgets:
            w.hide_all()

    def onShowButtonsOnly(self, _):
        for w in self._buttons_widgets:
            w.show_all()
        for w in self._joints_widgets:
            w.hide_all()

    def setWalkConfig(self, arg):
        self._walkconfig = arg

    def onDestroy(self, *args):
        print "quitting.."
        reactor.stop()

    def toggleit(self, what, attrname):
        if getattr(self, attrname):
            what.hide()
            setattr(self, attrname, False)
        else:
            what.show()
            setattr(self, attrname, True)

    def toggleVision(self, w):
        if self.vision is None:
            import naovision
            self.vision = naovision.Main(self.con)
            self.vision_visible = True
            return
        self.toggleit(self.vision.w, 'vision_visible')

    def toggleInertial(self, w):
        if self.inertial is None:
            self.inertial = Inertial(self.con)
            self.inertial_visible = True
            return
        self.toggleit(self.inertial.w, 'inertial_visible')

    def toggleLocalization(self, w):
        if self.localization is None:
            self.localization = Localization(self.con)
            self.localization_visible = True
            return
        self.toggleit(self.localization.w, 'localization_visible')

    def getAngles(self):
        """ TODO: callback from twisted
        """
        self.con.ALMotion.getBodyAngles().addCallback(self.onNewAngles)

    def onNewAngles(self, new_angles):
        self.cur_read_angles = new_angles
        for joint, angle in zip(self.joint_names, new_angles):
            self.scales[joint].state_scale.set_value(angle)

    def setStiffnessOn(self, w):
        self.con.ALMotion.setBodyStiffness(0.8)

    def setStiffnessOff(self, w):
        self.con.ALMotion.setBodyStiffness(0.0)

    def printAngles(self, w):
        j = self.cur_read_angles
        print repr([j[2:6], j[8:14], j[14:20], j[20:24]])

if __name__ == '__main__':
    main = Main()
    reactor.run()
    #import pdb; pdb.set_trace()

