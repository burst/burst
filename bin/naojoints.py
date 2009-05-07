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
from burst_util import cached

DT_CHECK_FOR_NEW_ANGLES = 0.2 # seconds between socket calls

@cached('joint_data.pickle')
def getJointData(con):
    joint_names = con.ALMotion.getBodyJointNames()
    joint_limits = dict([(joint_name, con.ALMotion.getJointLimits(joint_name)) for joint_name in joint_names])
    return (joint_names, joint_limits)

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
                print "joint, %s, value %s %s" % (joint_name, s.get_value(), val)
                con.ALMotion.setAngle(self.name, val)
                
        self.scales = scales = {}
        self.con = pynaoqi.getDefaultConnection()
        con = self.con
        self.vision = None
        self.joint_names, self.joint_limits = getJointData(self.con)
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
            ]:
            b = gtk.Button(label)
            b.connect('clicked', cb)
            button_box.add(b)
        c.pack_start(button_box, False, False, 0)

        # Create the joint controlling and displaying slides

        c.add(table)
        cur_angles = self.con.ALMotion.getBodyAngles()
        for i, (joint_name, cur_a) in enumerate(zip(self.joint_names, cur_angles)):
            min_val, max_val, max_change_per_step = self.joint_limits[joint_name]
            s = Scale(i, joint_name, min_val, max_val, cur_a)
            scales[joint_name] = s
            both = gtk.FILL | gtk.EXPAND
            for (row, obj), (xoptions, yoptions) in zip(enumerate(s.col), [(0, 0), (0, 0), (both, both)]):
                table.attach(obj, i, i+1, row, row+1, xoptions, yoptions)
            # value-changed is raised also when set_value is called
            # move-scaler - nothing?
        w.resize(700, 400)
        w.show_all()
        w.connect("destroy", gtk.main_quit)
        self.updater = task.LoopingCall(self.getAngles)
        self.updater.start(DT_CHECK_FOR_NEW_ANGLES)

    def toggleVision(self, w):
        if self.vision is None:
            import naovision
            self.vision = naovision.Main(self.con)
            self.vision_visible = True
            return
        if self.vision_visible:
            self.vision.w.hide()
            self.vision_visible = False
        else:
            self.vision.w.show()
            self.vision_visible = True

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

