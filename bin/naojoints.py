#!/usr/bin/python

# add path to burst lib
import os
import sys

from twisted.internet import gtk2reactor
# gtk2reactor must happen before importing burst - FIXME
try:
    gtk2reactor.install()
except:
    pass

if not 'AL_DIR' in os.environ:
    os.environ['AL_DIR'] = '/usr/local/nao'
    print "warning: $AL_DIR not defined, defining to %s" % os.environ['AL_DIR']

burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)
from burst_consts import ROBOT_IP_TO_NAME
from burst_util import set_robot_ip_from_argv

def main():
    import pynaoqi
    import pynaoqi.widgets
    import pynaoqi.gui
    options = pynaoqi.getDefaultOptions()
    if options.notes:
        clazz = pynaoqi.widgets.NotesWindow
    elif options.video:
        clazz = pynaoqi.widgets.VideoWindow
    elif options.calibrator:
        clazz = pynaoqi.widgets.Calibrator
    else:
        clazz = pynaoqi.gui.Joints
    pynaoqi.gui.main(clazz)

if __name__ == '__main__':
    set_robot_ip_from_argv()
    main()

