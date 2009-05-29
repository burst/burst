import time

import gtk, goocanvas

from twisted.internet.defer import Deferred, succeed

from pynaoqi.consts import *
from pynaoqi import options

try:
    import matplotlib
    from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar
    from matplotlib.pylab import Figure
except:
    pass

from burst.consts import DEG_TO_RAD, RAD_TO_DEG
import burst.consts as consts

#############################################################################

class BaseWindow(object):

    """ Any window we shall open, any widget """

    counter = 1

    def __init__(self):
        self._title = 'base'
        self._w = w = gtk.Window()
        w.connect("delete-event", self._onDestroy)
        self.counter += 1

    def _onDestroy(self, target, event):
        self._w.destroy()

    def show(self):
        self._w.show()

    def hide(self):
        self._w.hide()


class TaskBaseWindow(BaseWindow):

    """ Any widget that is based on some timer based update """

    loggers = []

    def __init__(self, tick_cb, title=None, dt=1.0):
        super(TaskBaseWindow, self).__init__()
        from twisted.internet import task
        if title is None:
            title = '%s %s' % (options.ip, self.counter)
        self._title = title
        self._dt = dt
        self._tick_cb = tick_cb
        self._start = time.time() # updated at the real start, _startTaskFirstTime
        self._task = task.LoopingCall(self._onLoop)
        self.loggers.append(self)
        self.set_title()

    def _startTaskFirstTime(self):
        self._start = time.time()
        self.start()
        self.set_title()
    # Task Methods

    def stop(self):
        if self._task.running:
            self._task.stop()
            self.set_title()

    def start(self):
        if not self._task.running:
            self._task.start(self._dt)
            self.set_title()

    @classmethod
    def startAll(self):
        for f in self.loggers:
            if not f._task.running:
                f.start()

    @classmethod
    def stopAll(self):
        for f in self.loggers:
            if f._task.running:
                f.stop()

    # GUI Methods
    def set_title(self, txt=None):
        if txt is None:
            txt = self._title
        self._w.set_title('%s - %s' % (
            self._task.running and 'running' or 'stopped', txt))
        self._title = txt

    def _onDestroy(self, target, event):
        print "stopping task"
        self.stop()
        super(TaskBaseWindow, self)._onDestroy(target, event)

    # Timer Methods

    def _onLoop(self):
        #if not self._w.is_active(): return
        d = self._tick_cb()
        if d and hasattr(d, 'addCallback'):
            d.addCallback(self._update)
        else:
            raise Exception("TaskBaseWindow: tick_cb must return a deferred")

    def _update(self, result):
        print "TaskBaseWindow: got %s" % result

# Plotting / Logging utils - yeah, I should use matplotlib.. but this is actually
# simple.
class GtkTextLogger(TaskBaseWindow):
    """ A simple widget to log output of a callback over time,
    using text (not graphical, just a ticker scrolling).
    """

    """
    @tick_cb - function that returns the value to display, preferably
    as a string. (if not str is called on it). Will be called repeatedly.
    @dt - time between calls.
    @title - title of window.
    """
    def __init__(self, tick_cb, title=None, dt=1.0):
        super(GtkTextLogger, self).__init__(tick_cb=tick_cb, title=title, dt=dt)
        self._tv = tv = gtk.TextView()
        self._tb = tb = gtk.TextBuffer()
        self._sw = gtk.ScrolledWindow()
        self._sw.add(self._tv)
        self._w.add(self._sw)
        self._w.set_size_request(300,300)
        self._w.show_all()
        tv.set_buffer(tb)
        self._values = []
        self._times = []
        self._startTaskFirstTime()

    def _update(self, result):
        #if not self._w.is_active(): return
        tb = self._tb
        t = time.time() - self._start
        self._times.append(t)
        self._values.append(result)
        tb.insert(tb.get_start_iter(), '%3.3f: %s\n' % (t, str(result)))

    def plotme(self):
        from pylab import plot, array
        plot(array(self._times), array(self._values))

def make_ellipse(parent, x, y, radius, fill_color):
    return goocanvas.Ellipse(parent = parent,
            center_x = x, center_y = y,
            radius_x = radius, radius_y = radius,
            fill_color = fill_color)

def make_rect(parent, x, y, width, height, fill_color):
    return goocanvas.Rect(parent = parent,
            x = x, y = y,
            width = width, height = height,
            fill_color = fill_color)

class CanvasTicker(TaskBaseWindow):
    """ Draw many things against a single canvas """

    # Last gimmik. Really.

    def __init__(self, tick_cb, limits, statics=None, title=None, dt=1.0):
        super(CanvasTicker, self).__init__(tick_cb=tick_cb, title=title, dt=dt)
        self._field = goocanvas.Canvas()
        self._field.set_size_request(400, 400)
        self._limits = limits # left, right, bottom, top
        self._objects = []
        self._radius = 3
        self._w.add(self._field)
        self._w.show_all()
        self._root = root = self._field.get_root_item()
        self._rect = goocanvas.Rect(parent=self._root)
        self._on_screen_resize()
        # Safe to use results_to_screen now
        if statics: # TODO - updates on screen resize
            self._statics = statics
            self._static_objects = []
            for static in statics:
                if len(static) == 4: # circle
                    _x, _y, _r, color = static
                    x, y = self.results_to_screen(_x, _y)
                    obj = make_ellipse(parent=self._root,
                        x=x, y=y, radius=_r, fill_color=color)
                else: # rectangle
                    ((_x, _y), _width, _height), color = static
                    x, y = self.results_to_screen(_x, _y)
                    width, height = self.width_height_to_screen(
                        _width, _height)
                    obj = make_rect(parent=self._root,
                        x=x, y=y, width=width, height=height,
                            fill_color=color)
                self._static_objects.append(obj)
        self._startTaskFirstTime()

    def _on_screen_resize(self):
        width, height = self._w.get_size()
        res_width = self._limits[1] - self._limits[0]
        res_height = self._limits[3] - self._limits[2]
        self._xf = float(width) / res_width
        self._yf = float(height) / res_height
        limits = self._limits
        x1, y1 = self.results_to_screen(limits[0], limits[2])
        x2, y2 = self.results_to_screen(limits[1], limits[3])
        self._rect.set_properties(x=x1, y=y1,
            width=x2-x1, height = y2-y1)

    def results_to_screen(self, x, y):
        left, right, bottom, top= self._limits
        if not (left <= x <= right) or not (bottom <= y <= top):
            print "CanvasTicker: object out of bounds (%3.3f %3.3f %3.3f %3.3f): x=%3.3f, y=%3.3f" % (
                left, right, bottom, top, x, y)
        return self._xf * (x - left), self._yf * (y - bottom)

    def width_height_to_screen(self, width, height):
        return self._xf * width, self._yf * height

    def _update(self, results):
        fill_color = 'black'
        radius = self._radius
        parent = self._root
        if len(self._objects) != len(results):
            self._objects = [goocanvas.Ellipse(parent = parent,
                center_x = 0, center_y = 0,
                radius_x = radius, radius_y = radius,
                fill_color = fill_color)
                    for x, y, in results]
        for (res_x, res_y), obj in zip(results, self._objects):
            x, y = self.results_to_screen(res_x, res_y)
            obj.set_properties(center_x=x, center_y=y)

class PlottingWindow(BaseWindow):

    def __init__(self):
        super(PlottingWindow, self).__init__()
        self._fig = fig = Figure()
        self._gtkfig = FigureCanvasGTK(fig)
        self._w.add(self._gtkfig)
        self._w.set_size_request(300, 300)
        self._w.show_all()

class GtkTimeTicker(TaskBaseWindow):
    """ plot against time a specific item / set of items
    Only works on arrays - so no singles!
    """
    def __init__(self, tick_cb, title=None, dt=1.0, len=100, limits=None):
        super(GtkTimeTicker, self).__init__(tick_cb=tick_cb, title=title, dt=dt)
        self._no_given_limits = limits is None
        self._len = len
        self._fig = fig = Figure()
        self._axis = axis = fig.add_subplot(111)
        self._times = []
        self._values = []
        self._lines = []
        self._gtkfig = FigureCanvasGTK(fig)
        self._w.add(self._gtkfig)
        self._w.set_size_request(300, 300)
        self._w.show_all()
        self._min_y, self._max_y = 0.0, 0.0
        self._limits = limits
        if limits:
            self.setYLimits(*limits)
        self._startTaskFirstTime()

    def _update(self, result):
        if len(result) == 0:
            print "GtkTimeTicker: empty length result, nothing to do\r\n"
            return
        if len(result) > len(self._lines):
            print "updating GtkTimeTicker to %s lines" % len(result)
            for i in xrange(len(result) - len(self._lines)):
                self._lines.append(self._axis.plot([],[])[0])
            if len(self._values) != len(result):
                # strange feature - if a new plot is added erase the old ones.
                self._values = [[] for i in xrange(len(result))]
            if self._limits:
                self.setYLimits(*self._limits)

        self._min_y, self._max_y = min(self._min_y, *result), max(self._max_y, *result)
        self._times.append(time.time() - self._start)
        for i, v in enumerate(result):
            self._values[i].append(v)
        if len(self._values[0]) > self._len:
            for values in self._values:
                del values[:(len(values) - self._len)]
            del self._times[:(len(self._times) - self._len)]
        self.updatePlot()

    def updatePlot(self):
        # TODO - better way then resetting the whole number of points.
        for line, values in zip(self._lines, self._values):
            line.set_data(self._times, values)
            if len(line._x) != len(line._y):
                import pdb; pdb.set_trace()
        self._axis.set_xlim(self._times[0], self._times[-1])
        if self._no_given_limits:
            self.setYLimits(self._min_y, self._max_y)
        self._gtkfig.draw()

    def setYLimits(self, lim_min, lim_max):
        self._axis.set_ylim(lim_min, lim_max)

class VideoWindow(TaskBaseWindow):

    def __init__(self, con):
        if con.has_imops() is None:
            print "Video window not opened, imops isn't working, please fix"
            return
        self._con = con
        self._con.registerToCamera().addCallback(self._finishInit)
        super(VideoWindow, self).__init__(tick_cb=self.getNew, dt=0.5)
        self._im = gtkim = gtk.Image()
        # you don't get button press on gtk.Image(), setting add_events on window
        # and gtkim doesn't cause propogation, don't know what does.
        self._dmove = succeed(None)
        self._w.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self._w.connect("button-press-event", self._onButtonClick)
        self._w.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self._w.connect("motion-notify-event", self._onMouseMotion)
        self._w.add(gtkim)
        self._w.show_all()

    def _finishInit(self, result):
        self._startTaskFirstTime()

    def _updateTarget(self, x, y):
        """ x and y in pixels in 0~IMAGE_WIDTH-1, 0~IMAGE_HEIGHT-1 range
        target for yaw is positive if x is to the left of the picture, as then
        the change would have been negative
        """
        self._target = ((consts.IMAGE_HALF_WIDTH - x) * consts.PIX_TO_RAD_X
                , (y - consts.IMAGE_HALF_HEIGHT) * consts.PIX_TO_RAD_Y)

    def _onMouseMotion(self, widget, event):
        self._updateTarget(event.x, event.y)
        yaw, pitch = self._target
        self.set_title('%s, %s (%d, %d)' % (
            event.x, event.y, int(yaw*RAD_TO_DEG), pitch*RAD_TO_DEG))

    def _onButtonClick(self, widget, event):
        print "click: ", event.x, event.y
        if not self._dmove.called: return
        self._updateTarget(event.x, event.y)
        self._dmove = Deferred() # to be replaced later
        MIN_PITCH_MOVE = MIN_YAW_MOVE = 3 * DEG_TO_RAD
        cmd_yaw, cmd_pitch = self._target
        if abs(cmd_yaw) > MIN_YAW_MOVE or abs(cmd_pitch) > MIN_PITCH_MOVE:
            #print "commanding: yaw %3.3f, pitch %3.3f" % (cmd_yaw*RAD_TO_DEG, cmd_pitch*RAD_TO_DEG)
            self._dmove = Deferred()
            self._con.ALMotion.getBodyAngles().addCallback(self._onButtonClick_onBodyAngles)

    def _onButtonClick_onBodyAngles(self, result):
        yaw, pitch = result[consts.HEAD_YAW_JOINT_INDEX], result[consts.HEAD_PITCH_JOINT_INDEX]
        cmd_yaw, cmd_pitch = self._target
        tgt_yaw, tgt_pitch = yaw + cmd_yaw, pitch + cmd_pitch
        print "moving yaw %3.1f->%3.1f, pitch %3.1f->%3.1f" % (yaw*RAD_TO_DEG, pitch*RAD_TO_DEG,
            tgt_yaw*RAD_TO_DEG, tgt_pitch*RAD_TO_DEG)
        self._dmove = self._con.ALMotion.gotoAnglesWithSpeed(
            ['HeadYaw', 'HeadPitch'], [tgt_yaw, tgt_pitch],
            50, # percent of max speed 1~100
            consts.INTERPOLATION_SMOOTH)

    def getNew(self):
        #import pdb; pdb.set_trace()
        return self._con.getRGBRemoteFromYUV422()

    def _update(self, result):
        width, height, rgb = result
        pixbuf = gtk.gdk.pixbuf_new_from_data(rgb, gtk.gdk.COLORSPACE_RGB, False, 8, width, height, width*3)
        self._im.set_from_pixbuf(pixbuf)

################################################################################

def maxmin():
    val = yield()
    themin = val
    themax = val
    while True:
        val = yield(themin, themax)
        themin, themax = min(themin, val), max(themax, val)

class MyCircle(object):
    """ Normalize coordinates
    """
    _screen_x, _screen_y = LOC_SCREEN_X_SIZE, LOC_SCREEN_Y_SIZE
    _xf, _yf = _screen_x / fol, _screen_y / fow # 1/cm
    print "XF = %s, YF = %s" % (_xf, _yf)
    # The position of the center on screen point, in local (field, set_x/set_y) coordinates
    _cx, _cy = 0.5 * fol, 0.5 * fow
    _cx_screen, _cy_screen = _screen_x / 2, _screen_y / 2

    @classmethod
    def fromCircle(cls, ex):
        el = ex._ellipse
        c = MyCircle(parent = el.get_parent(),
            center_x = ex._x,
            center_y = ex._y,
            radius = ex._radius,
            fill_color = ex._fill_color)
        return c

    def __init__(self, parent, center_x, center_y, radius,
        fill_color):
        _cx, _cy, _xf, _yf = self._cx, self._cy, self._xf, self._yf
        self._ellipse = goocanvas.Ellipse(parent = parent,
            center_x = 0.0, center_y = 0.0,
            radius_x = radius * _xf, radius_y = radius * _yf,
            fill_color = fill_color)
        self._radius = radius
        self._fill_color = fill_color
        self._x = center_x
        self._y = center_y
        self.set_x(center_x)
        self.set_y(center_y)
        self.maxmin_x = maxmin()
        self.maxmin_x.next()
        self.maxmin_y = maxmin()
        self.maxmin_y.next()

    def get_x(self):
        return self._x

    def get_screen_x(self):
        return (self._x - self._cx) * self._xf + self._cx_screen

    def set_x(self, x):
        self._x = x
        if hasattr(self, 'maxmin_x'):
            self.maxmin_x_val = self.maxmin_x.send(x)
        self._ellipse.set_property('center-x', self.get_screen_x())

    def get_y(self):
        return self._y

    def get_screen_y(self):
        return (self._y - self._cy) * self._yf + self._cy_screen
    
    def set_y(self, y):
        self._y = y
        if hasattr(self, 'maxmin_y'):
            self.maxmin_y_val = self.maxmin_y.send(y)
        self._ellipse.set_property('center-y', self.get_screen_y())

    x = property(get_x, set_x)
    y = property(get_y, set_y)

class Localization(object):

    def __init__(self, con):
        self.con = con
        self.w = w =gtk.Window()
        self.status = 'started'
        self.set_title()
        c = gtk.VBox()
        w.add(c)
        self.field = goocanvas.Canvas()
        self.field.set_size_request(LOC_SCREEN_X_SIZE, LOC_SCREEN_Y_SIZE)
        c.add(self.field)
        self.objects = []
        self.snapshots = []
        self.root = root = self.field.get_root_item()
        for color, x, y in [
            ('blue', BGLP_X, BGLP_Y),
            ('blue', BGRP_X, BGRP_Y),
            ('yellow', YGLP_X, YGLP_Y),
            ('yellow', YGRP_X, YGRP_Y),
            ('orange', 0, 0),
            ('black', FIELD_OUTER_LENGTH/4, 0)]:
            obj = MyCircle(parent = root,
                center_x = x, center_y = y, radius = 5,
                fill_color = color)
            self.objects.append(obj)
        self.robot = self.objects[-1]
        self.ball  = self.objects[-2]
        snapshot = gtk.Button('snapshot')
        snapshot.connect('clicked', self.onSnapshot)
        c.pack_start(snapshot, False, False, 0)

        self._pairs = []
        self.localized = {}
        for v in localization_vars:
            _, __, ___, obj, key = v.split('/')
            if obj not in self.localized:
                self.localized[obj] = {}
            if key not in self.localized[obj]:
                self.localized[obj][key] = 0.0
            self._pairs.append((obj, key))

        w.show_all()
        self.vars = localization_vars
        con.modulesDeferred.addCallback(self.installUpdater)

    def set_title(self):
        self.w.set_title('localization - %s - %s' % (self.con.host, self.status))

    def installUpdater(self, _):
        self.updater = task.LoopingCall(self.getVariables)
        self.updater.start(DT_CHECK_FOR_NEW_INERTIAL)

    def getVariables(self):
        self.con.ALMemory.getListData(self.vars).addCallback(self.updateField)

    def onSnapshot(self, name=None):
        # TODO - different color, filters
        self.snapshots.append([])
        for i in xrange(4,6):
            self.snapshots[-1].append(MyCircle.fromCircle(self.objects[i]))

    def updateField(self, vals):
        """ localization values are in centimeters """
        for (obj, key), v in zip(self._pairs, vals):
            self.localized[obj][key] = v
        read = (self.localized['Ball']['XEst'],
                self.localized['Ball']['YEst'],
                self.localized['Self']['XEst'],
                self.localized['Self']['YEst'])
        try:
            self.status = "%3.3f %3.3f %3.3f %3.3f" % read
            self.set_title()
        except:
            self.status = 'no reading'
            self.set_title()
            return
        self.ball.x, self.ball.y, self.robot.x, self.robot.y = read
        #print 'screen: %3.3f %3.3f %3.3f %3.3f' % (self.ball.get_screen_x(), self.ball.get_screen_y(), self.robot.get_screen_x(), self.robot.get_screen_y())
        #print "ball:   %s, %s" % (self.ball.maxmin_x_val, self.ball.maxmin_y_val)


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


