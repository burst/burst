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
from pynaoqi.widgets import Localization, Inertial, BaseWindow
from pynaoqi.consts import LOC_SCREEN_X_SIZE, LOC_SCREEN_Y_SIZE
from burst_util import (cached, cached_deferred, Deferred, clip,
    DeferredList)

DT_CHECK_FOR_NEW_ANGLES   = 0.5 # seconds between socket calls
DT_CHECK_FOR_NEW_INERTIAL = 0.5
DT_CHECK_BATTERY_LEVEL    = 10.0

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
                d = con.ALMotion.gotoAngleWithSpeed(self.name, clip(-pi, pi, val), 50, 1)
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

# TODO - use burst.actions.Actions.setWalkConfig directly, don't copy.
def setWalkConfig(con, param):
    """ param should be one of the moves.WALK_X """
    (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude,
        LHipRoll, RHipRoll, HipHeight, TorsoYOrientation, StepLength, 
        StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY) = param[:]

    ds = []
    ds.append(con.ALMotion.setWalkArmsConfig( ShoulderMedian, ShoulderAmplitude,
                                        ElbowMedian, ElbowAmplitude ))
    ds.append(con.ALMotion.setWalkArmsEnable(True))

    # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
    ds.append(con.ALMotion.setWalkExtraConfig( LHipRoll, RHipRoll, HipHeight, TorsoYOrientation ))

    ds.append(con.ALMotion.setWalkConfig( StepLength, StepHeight, StepSide, MaxTurn,
                                                ZmpOffsetX, ZmpOffsetY ))

    return DeferredList(ds)

class ScalePane(object):

    """ single object with multiple scales, for easy hiding """

    def __init__(self, parent, name, table, start_joint_num, joints, cur_angles):
        self._name = name
        self._parent = parent
        self._joints = joints
        self._toggle = gtk.Button(self._name)
        self._toggle.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self._toggle.connect('button-press-event', self._onToggleClicked)
        self._visible = True
        # update visibility toggling lists
        self._widgets = []
        for i, (joint_name, cur_a) in enumerate(zip(joints, cur_angles)):
            start_i = start_joint_num + i
            min_val, max_val, max_change_per_step = self._parent.joint_limits[joint_name]
            s = Scale(start_i, joint_name, min_val, max_val, cur_a)
            parent.scales[joint_name] = s # for updating
            for (row, obj), (xoptions, yoptions) in zip(enumerate(s.col), Scale.ROW_OPTIONS):
                table.attach(obj, start_i, start_i+1, row, row+1, xoptions, yoptions)
            self._widgets.extend(s.col)
            # value-changed is raised also when set_value is called
            # move-scaler - nothing?

    def toggle(self):
        return self._toggle

    def _onToggleClicked(self, widget, event):
        if event.button == 2:
            {True:self.hide, False:self.show}[self._visible]()
        elif event.button == 3:
            self._parent.showAllJoints()
        else: # default
            self._parent.toggleAllJointPanesButOne(self)

    def show(self):
        for w in self._widgets:
            w.show_all()
        self._visible = True

    def hide(self):
        for w in self._widgets:
            w.hide()
        self._visible = False

def create_button_strip(data):
    """ despite the name this takes a iterable of (label, cb)
    where label can also be a constructed widget, if it isn't
    a string it is left untouched and added to a HBox as is,
    otherwise a button is constructed. If cb is not None then the
    clicked signal will call it.
    """
    button_box = gtk.HBox()
    buttons = []
    for label, cb in data:
        if cb is None and not isinstance(label, str):
            b = label # masquarade as a place to put premade widgets, for battery meter
        else:
            b = gtk.Button(label)
        if cb:
            b.connect("clicked", cb)
        try:
            button_box.add(b)
        except:
            import pdb; pdb.set_trace()
        buttons.append(b)
    return button_box, buttons

################################################################################
#### Main Class
################################################################################
class Joints(BaseWindow):

    def __init__(self):
        super(Joints, self).__init__()
        global start_time
        global con
        start_time = time()
              
        self.scales = scales = {}
        self.con = pynaoqi.getDefaultConnection(with_twisted=True)
        con = self.con
        self.updater = task.LoopingCall(self.getAngles)
        self.battery_level_task = task.LoopingCall(self.getBatteryLevel)

        self.vision = None
        self.inertial = None
        self.localization = None
        if pynaoqi.options.localization_on_start:
            self.toggleLocalization(None)

        # Create the joint controlling and displaying slides (called by onJointData)
        def onBodyAngles(cur_angles):
            self._joint_panes = []
            self._joints_table = table = gtk.Table(
                    rows=Scale.NUM_ROWS, columns=len(self.joint_names), homogeneous=False)
            # put all the toggle buttons on the top
            togglebox = gtk.HBox()
            for name, start, end in [('Head', 0,2), ('LArm', 2, 8), ('LLeg', 8, 14),
                    ('RLeg', 14, 20), ('RArm', 20, 26)]:
                joints, angles = self.joint_names[start:end], cur_angles[start:end]
                pane = ScalePane(parent=self, name=name, table=table, start_joint_num=start,
                    joints=joints, cur_angles=angles)
                self._joint_panes.append(pane)
                # update visibility toggling lists
                togglebox.add(pane.toggle())
            self._joints_container.pack_start(togglebox, False, False, 0)
            self._joints_container.add(table)
            self._joints_widgets.add(table)
            self._all_widgets.add(table)
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
        self.con.modulesDeferred.addCallback(lambda result:
            self.con.ALMotion.initDeferred.addCallback(lambda _: getJointData(self.con).addCallback(onJointData))
            )
        # initiate battery task when pynaoqi finishes loading
        self.con.modulesDeferred.addCallback(lambda _: self.battery_level_task.start(
            DT_CHECK_BATTERY_LEVEL))
        w = self._w
        w.set_title('naojoints - %s' % self.con.host)
        self.c = c = gtk.VBox()
        self._joints_container = gtk.VBox() # top - buttons, bottom - joints sliders table
        w.add(c)

        # Create Many Buttons on Top

        bat_stat_eventbox = gtk.EventBox()
        self._battery_level_button = battery_status_label = gtk.Label()
        bat_stat_eventbox.connect('button-press-event', self._toggleAllButtonsExceptBattery)
        bat_stat_eventbox.add(battery_status_label)

        top_buttons_data = [
            (bat_stat_eventbox,   None),
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
        import burst

        moves_buttons_data = [(move_name, lambda _, move=getattr(moves, move_name):
            self.con.ALMotion.executeMove(move))
                for move_name in moves.NAOJOINTS_EXECUTE_MOVE_MOVES]

        self._walkconfig = burst.moves.walks.STRAIGHT_WALK.walkParameters

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
            distance_per_step = self._walkconfig[0]
            return setWalkConfig(self.con, self._walkconfig).addCallback(
                lambda result: self.con.ALMotion.addWalkStraight(
                    steps * distance_per_step, 60).addCallback(startWalkTest)
                    )

        def doArc(angle, radius=0.5, cycles_per_step=60):
            # angle [rad], radius [m], # 20ms cycles per step
            return self.con.ALMotion.addWalkArc(
                angle, radius, cycles_per_step).addCallback(startWalkTest)

        def doTurn(angle, cycles_per_step=60):
            # angle [rad], # 20ms cycles per step
            return self.con.ALMotion.addTurn(
                angle, cycles_per_step).addCallback(startWalkTest)

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
            ('rt 45', lambda _, steps=1: doTurn(-pi / 4)),
            ('lt 45', lambda _, steps=-1: doTurn(pi / 4)),
            ('arc right 1', lambda _, steps=1: doArc( -1 )),
            ('arc left 1', lambda _, steps=-1: doArc(  1 )),
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
    
        # add the joints container after all the buttons
        c.add(self._joints_container)

        # lists for toggling visibility with appropriate callbacks
        self._buttons_widgets = set([stiffness_off, stiffness_on, moves_strip, walk_strip])
        self._joints_widgets = set([])
        self._all_widgets = self._buttons_widgets.union(self._joints_widgets)
        self._all_but_bat_label = self._all_widgets.union(set(top_buttons[1:]))

        w.resize(700, 400)
        w.show_all()
    
    def showAllJoints(self):
        for pane in self._joint_panes:
            pane.show()

    def toggleAllJointPanesButOne(self, show_pane):
        if show_pane:
            show_pane.show()
        for pane in self._joint_panes:
            if show_pane is not pane:
                pane.hide()
        # resize to minimize width
        self._w.resize(200, self._w.get_size()[1])

    def _toggleAllButtonsExceptBattery(self, widget, event, state=[True]):
        op = {True: lambda w: w.hide_all(),
         False: lambda w: w.show_all()}[state[0]]
        state[0] = not state[0]
        map(op, self._all_but_bat_label)

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

    def _onDestroy(self, *args):
        if self.updater.running:
            print "stopping joints task"
            self.updater.stop()
        super(Joints, self)._onDestroy(*args)

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

    def getBatteryLevel(self):
        self.con.ALSentinel.getBatteryLevel().addCallback(self._updateBatteryLevel)

    def _updateBatteryLevel(self, value):
         self._battery_level_button.set_markup(
            '<span foreground="%s">BAT %s</span>' % (value > 3 and 'green' or 'red', value))

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

