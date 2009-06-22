#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Show the images from the Nao using clutter.

Important Webots Note:

 You will get a blank image if you are not running with webots on the
same desktop screen - the way the image is computed in webots uses the GPU, and somehow doesn't
work when the webots app is not in the foreground and actually displays.

"""

import os
import math
from datetime import datetime
from time import time

import gobject
import cairo
import clutter
import cluttergtk # must be after clutter - otherwise you'll get a brokern event loop, no drawing
import cluttergst
from cluttercairo import CairoTexture
#import cluttergst

# add path to burst lib
import os
import sys
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi

class Main(object):

    WHICH_CAMERA = 1 # buttom = 1

    def __init__(self):
        self._con = con = pynaoqi.getDefaultConnection()
        options = pynaoqi.getDefaultOptions()
        broker_info = dict(con.getBrokerInfo())
        con.getInfo(broker_info['name'])
        con.registerBroker()
        con.exploreToGetModuleByName('NaoCam')
        con.registerToCamera()
        self._c = 0
        self._image = None
        self._initGui()

    def _initGui(self):
        if self.WHICH_CAMERA == 1:
            print "using bottom camera"
            self._con.switchToBottomCamera()
        else:
            print "using top camera"
            self._con.switchToTopCamera()
        stage_color = clutter.Color(0x99, 0xcc, 0xff, 0xff)

        stage = clutter.Stage()
        #stage.connect('button-press-event', clutter.main_quit)
        stage.connect('destroy', clutter.main_quit)
        stage.set_color(stage_color)
        stage.set_user_resizable(True)
        stage.set_size(400, 300)

        self._texture = texture = clutter.Texture('top.jpg')
        texture.set_position(0, 0)
        stage.add(texture)

        #tick(texture)
        gobject.timeout_add_seconds(1, self.onUpdateImage)
        stage.show()
        stage.show_all()
        self.stage = stage

    def getImage(self):
        self._image = self._con.getImageRemoteRGB()

    def onUpdateImage(self):
        texture = self._texture
        self.getImage()
        im, width, height = self._image
        print "%s: %s, %s" % (time() - start_time, width, height)
        texture.set_from_rgb_data(im, False, width, height, width*3, 3, 0)
        return True # required by gobject.timeout

start_time = time()

if __name__ == '__main__':
    main = Main()

    clutter.main()

