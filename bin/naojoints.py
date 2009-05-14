#!/usr/bin/python
from time import time

from twisted.internet import gtk2reactor

try:
    gtk2reactor.install()
except:
    pass

from twisted.internet import reactor, task
from twisted.internet.defer import succeed
from twisted.internet.threads import deferToThread

import gtk

# add path to burst lib
import os
import sys
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi
from burst_util import cached, cached_deferred, Deferred

DT_CHECK_FOR_NEW_ANGLES   = 0.5 # seconds between socket calls
DT_CHECK_FOR_NEW_INERTIAL = 0.5

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

class Main(object):

    def __init__(self):
        start_time = time()

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
                
        self.scales = scales = {}
        self.con = pynaoqi.getDefaultConnection(with_twisted=True)
        con = self.con
        self.vision = None
        self.inertial = None

        # Create the joint controlling and displaying slides (called by onJointData)
        def onBodyAngles(cur_angles):
            table = gtk.Table(rows=Scale.NUM_ROWS, columns=len(self.joint_names), homogeneous=False)
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
        w.set_title(self.con.host)
        self.c = c = gtk.VBox()
        w.add(c)

        # Create top buttons

        def create_button_strip(data):
            button_box = gtk.HBox()
            buttons = []
            for label, cb in data:
                b = gtk.Button(label)
                b.connect("clicked", cb)
                button_box.add(b)
                buttons.append(b)
            return button_box, buttons

        top_buttons_data = [
            ('print angles', self.printAngles),
            ('stiffness on', self.setStiffnessOn),
            ('stiffness off', self.setStiffnessOff),
            ('vision', self.toggleVision),
            ('inertial', self.toggleInertial),
            ]
        chains = ['Head', 'LLeg', 'LArm', 'RArm', 'RLeg']
        stiffness_off_buttons_data = [
                ('%s OFF' % chain,
                    lambda _, chain=chain: self.con.ALMotion.setChainStiffness(chain, 0.0))
                for chain in chains]
        stiffness_on_buttons_data = [
                ('%s on' % chain,
                    lambda _, chain=chain: self.con.ALMotion.setChainStiffness(chain, 0.0))
                for chain in chains]
        import burst.moves as moves
        moves_buttons_data = [(move_name, lambda _, move=getattr(moves, move_name):
            self.con.ALMotion.executeMove(move))
                for move_name in moves.NAOJOINTS_EXECUTE_MOVE_MOVES]
        c.pack_start(create_button_strip(top_buttons_data)[0], False, False, 0)
        stiffness_off, self.stiffness_off_buttons = (
            create_button_strip(stiffness_off_buttons_data))
        stiffness_on, self.stiffness_on_buttons = create_button_strip(stiffness_on_buttons_data)
        c.pack_start(stiffness_off, False, False, 0)
        c.pack_start(stiffness_on, False, False, 0)
        c.pack_start(create_button_strip(moves_buttons_data)[0], False, False, 0)

        # Create walk buttons (later need to allow hiding them)
        button_box = gtk.HBox()

        w.resize(700, 400)
        w.show_all()
        w.connect("destroy", self.onDestroy)
    
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

