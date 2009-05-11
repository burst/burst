#!/usr/bin/python
from time import time

from twisted.internet import gtk2reactor

try:
    gtk2reactor.install()
except:
    pass

from twisted.internet import reactor, task
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
        def store_one(jointname, result):
            results[jointname] = result
            if len(results) == len(joint_names):
                # finally!
                collecting.callback((joint_names, results))
        for joint_name in joint_names:
            con.ALMotion.getJointLimits(joint_name).addCallback(lambda result: store_one(joint_name, result))

    con.ALMotion.getBodyJointNames().addCallback(collect_callback)

    return collecting

class Inertial(object):

    def __init__(self, con):
        self.con = con
        self.w = w =gtk.Window()
        w.set_title(con.host)
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
            
            MIN_TIME_BETWEEN_CHANGES = 0.1 # throtelling - seems I make nao's stuck? naoqi problem?

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
                self.lowbox = gtk.HBox()
                self.lowbox.add(self.set_scale)
                self.lowbox.add(self.state_scale)
                self.col = [self.toplabel, self.label, self.lowbox]
                #self.box.pack_start(self.toplabel, False, False, 0)

            def onChanged(self, w, scroll_type, val):
                cur = time()
                if cur - self.last_sent_time < Scale.MIN_TIME_BETWEEN_CHANGES:
                    return
                self.last_sent_value = cur
                s = self.set_scale
                # TODO: throtlling?
                print "joint, %s, value %s %s" % (self.name, s.get_value(), val)
                # name, value, speed percent [0-100], interpolation (1 = smooth)
                con.ALMotion.gotoAngleWithSpeed(self.name, val, 50, 1)
                
        self.scales = scales = {}
        self.con = pynaoqi.getDefaultConnection()
        con = self.con
        self.vision = None
        self.inertial = None
        def onJointData(results):
            self.joint_names, self.joint_limits = results
        getJointData(self.con).addCallback(onJointData)
        w = gtk.Window()
        c = gtk.VBox()
        table = gtk.Table(rows=3, columns=len(self.joint_names), homogeneous=False)
        w.add(c)

        # Create top buttons

        button_box = gtk.HBox()
        for label, cb in [
            ('print angles', self.printAngles),
            ('stiffness on', self.setStiffnessOn),
            ('stiffness off', self.setStiffnessOff),
            ('vision', self.toggleVision),
            ('inertial', self.toggleInertial),
            ]:
            b = gtk.Button(label)
            b.connect('clicked', cb)
            button_box.add(b)
        c.pack_start(button_box, False, False, 0)

        # Create the joint controlling and displaying slides

        c.add(table)
        def onBodyAngles(cur_angles):
            for i, (joint_name, cur_a) in enumerate(zip(self.joint_names, cur_angles)):
                min_val, max_val, max_change_per_step = self.joint_limits[joint_name]
                s = Scale(i, joint_name, min_val, max_val, cur_a)
                scales[joint_name] = s
                both = gtk.FILL | gtk.EXPAND
                for (row, obj), (xoptions, yoptions) in zip(enumerate(s.col), [(0, 0), (0, 0), (both, both)]):
                    table.attach(obj, i, i+1, row, row+1, xoptions, yoptions)
                # value-changed is raised also when set_value is called
                # move-scaler - nothing?
            self.updater = task.LoopingCall(self.getAngles)
            self.updater.start(DT_CHECK_FOR_NEW_ANGLES)

        self.con.ALMotion.getBodyAngles().addCallback(onBodyAngles)
        w.resize(700, 400)
        w.show_all()
        w.connect("destroy", gtk.main_quit)

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
        new_angles = self.con.ALMotion.getBodyAngles()
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

