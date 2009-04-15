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

from mysoap import NaoQiConnection

class Main(object):

    def __init__(self, url):
        self._con = con = NaoQiConnection(url)
        broker_info = dict(con.getBrokerInfo())
        con.getInfo(broker_info['name'])
        con.registerBroker()
        con.exploreToGetModuleByName('NaoCam')
        con.registerToCamera()
        self._c = 0

    def getImage(self):
        con = self._con
        meths = (lambda: (con.switchToBottomCamera(), con.getImageRemoteRGB()),
             lambda: (con.switchToTopCamera(), con.getImageRemoteRGB()))
        im = meths[self._c]()
        self._c = 1 - self._c
        return im[1]

start_time = time()

def tick(texture):
    im, width, height = main.getImage()
    print "%s: %s, %s" % (time() - start_time, width, height)
    #import pdb; pdb.set_trace()
    # second: has_alpha_channel (False means no, just RGB)
    # last three: row stride in bytes, BytesPerPixel, Flags.
    texture.set_from_rgb_data(im, False, width, height, width*3, 3, 0)
    return True

if __name__ == '__main__':
    stage_color = clutter.Color(0x99, 0xcc, 0xff, 0xff)
    
    stage = clutter.Stage()
    stage.connect('button-press-event', clutter.main_quit)
    stage.connect('destroy', clutter.main_quit)
    stage.set_color(stage_color)
    stage.set_user_resizable(True)
    stage.set_size(200, 200)
    
    texture = clutter.Texture('top.jpg')
    #texture.set_size(300, 300)
    texture.set_position(0, 0)
    #texture.set_from_file('top.jpg')
    stage.add(texture)
    texture.show()
    #import pdb; pdb.set_trace()
    
    #tick(texture)
    gobject.timeout_add_seconds(1, tick, texture)
    stage.show()
    stage.show_all()
    
    import sys
    url = "http://localhost:9560/"
    if len(sys.argv) > 1:
        url = sys.argv[-1]
    print "using url =", url

    main = Main(url)

    clutter.main()

