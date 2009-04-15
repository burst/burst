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
        self._images = [None, None]
        self._initGui()

    def _initGui(self):
        stage_color = clutter.Color(0x99, 0xcc, 0xff, 0xff)
        
        stage = clutter.Stage()
        stage.connect('button-press-event', clutter.main_quit)
        stage.connect('destroy', clutter.main_quit)
        stage.set_color(stage_color)
        stage.set_user_resizable(True)
        stage.set_size(400, 200)
        
        self._textures = []
        for i in range(2):
            texture = clutter.Texture('top.jpg')
            #texture.set_size(300, 300)
            texture.set_position(i*200, 0)
            #texture.set_from_file('top.jpg')
            stage.add(texture)
            #import pdb; pdb.set_trace()
            self._textures.append(texture)
            
        #tick(texture)
        gobject.timeout_add_seconds(1, self.onUpdateImage)
        stage.show()
        stage.show_all()
        self.stage = stage
 
    def getBottomImage(self):
        self._con.switchToBottomCamera()
        self._images[0] = self._con.getImageRemoteRGB()

    def getTopImage(self):
        self._con.switchToTopCamera()
        self._images[1] = self._con.getImageRemoteRGB()

    def onUpdateImage(self):
        i = self._c
        self._c = 1 - self._c
        texture = self._textures[i]
        [self.getBottomImage, self.getTopImage][i]()
        im, width, height = self._images[i]
        print "%s: %s, %s" % (time() - start_time, width, height)
        texture.set_from_rgb_data(im, False, width, height, width*3, 3, 0)
        return True # required by gobject.timeout

start_time = time()

if __name__ == '__main__':
   
    import sys
    url = "http://localhost:9560/"
    if len(sys.argv) > 1:
        url = sys.argv[-1]
    print "using url =", url

    main = Main(url)

    clutter.main()

