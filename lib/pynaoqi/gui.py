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
from pynaoqi.widgets import Localization, Inertial
from pynaoqi.consts import LOC_SCREEN_X_SIZE, LOC_SCREEN_Y_SIZE
from burst_util import cached, cached_deferred, Deferred

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

class Joints(object):

    def __init__(self):
        global start_time
        global con
        start_time = time()
              
        self.scales = scales = {}
        self.con = pynaoqi.getDefaultConnection(with_twisted=True)
        con = self.con
        self.updater = task.LoopingCall(self.getAngles)
        self.vision = None
        self.inertial = None
        self.localization = None
        if pynaoqi.options.localization_on_start:
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

        # XXX - import burst here so it doesn't parse sys.argv
        import burst.moves as moves

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
        if self.updater.running:
            print "stopping joints task"
            self.updater.stop()

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

class JointsMain(Joints):

    def onDestroy(self, *args):
        super(JointsMain, self).onDestroy()
        print "quitting.."
        reactor.stop()

def main():
    joints = JointsMain()
    reactor.run()

if __name__ == '__main__':
    main()

