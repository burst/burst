#!/usr/bin/python
from twisted.internet import gtk2reactor

gtk2reactor.install()

from twisted.internet import reactor, task
from twisted.internet.threads import deferToThread

import gtk

# add path to burst lib
import os
import sys
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi

def getJointData(con):
    joint_names = con.ALMotion.getBodyJointNames()
    joint_limits = dict([(joint_name, con.ALMotion.getJointLimits(joint_name)) for joint_name in joint_names])
    return (joint_names, joint_limits)

pickle_file = 'joint_data.pickle'
def cachedJointData(con):
    import os, cPickle
    if not os.path.exists(pickle_file):
        # write pickle
        failed, fd = False, None
        try:
            fd = open(pickle_file, 'w+')
            cPickle.dump(getJointData(con), fd)
        except Exception, e:
            failed = True
        finally:
            if fd:
                fd.close()
        if failed:
            os.unlink(pickle_file)
    # read pickle
    fd = open(pickle_file)
    data = cPickle.load(fd)
    fd.close()
    return data

class Main(object):

    def __init__(self):
        self.slides = slides = {}
        self.con = pynaoqi.NaoQiConnection()
        self.joint_names, self.joint_limits = cachedJointData(self.con)
        w = gtk.Window()
        c = gtk.HBox()
        w.add(c)
        for joint_name in self.joint_names:
            min_val, max_val, max_change_per_step = self.joint_limits[joint_name]
            range_val = max_val - min_val
            step = range_val / 100.0
            page_step = range_val / 10.0
            page_size = page_step
            adj = gtk.Adjustment(min_val, min_val, max_val, step, page_step, page_size)
            s = gtk.VScale(adj)
            c.add(s)
            slides[joint_name] = s
            # value-changed is raised also when set_value is called
            # move-slider - nothing?
            s.connect("change-value", lambda w, scroll_type, val, self=self, joint_name=joint_name: self.onSlideChanged(joint_name))
        w.resize(600, 400)
        w.show_all()
        w.connect("destroy", gtk.main_quit)
        self.updater = task.LoopingCall(self.getAngles)
        self.updater.start(0.2)

    def onSlideChanged(self, joint_name):
        s = self.slides[joint_name]
        # TODO: throtlling?
        print "joint, %s, value %s" % (joint_name, s.get_value())
        self.con.ALMotion.setAngle(joint_name, s.get_value())

    def getAngles(self):
        """ TODO: callback from twisted
        """
        new_angles = self.con.ALMotion.getBodyAngles()
        for joint, angle in zip(self.joint_names, new_angles):
            self.slides[joint].set_value(angle)

if __name__ == '__main__':
    main = Main()
    reactor.run()

