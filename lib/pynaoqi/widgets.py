import time

import gtk, goocanvas

from pynaoqi.consts import *
from pynaoqi import options

try:
    import matplotlib
    from matplotlib.backends.backend_gtk import FigureCanvasGTK
    from matplotlib.pylab import Figure
except:
    pass

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
        self._startTaskFirstTime()

    def _update(self, result):
        #if not self._w.is_active(): return
        tb = self._tb
        tb.insert(tb.get_start_iter(), '%3.3f: %s\n' % (
            (time.time() - self._start), str(result)))

class CanvasTicker(TaskBaseWindow):
    """ Draw many things against a single canvas """

    # Last gimmik. Really.

    def __init__(self, tick_cb, limits, title=None, dt=1.0):
        super(CanvasTicker, self).__init__(tick_cb=tick_cb, dt=dt)
        self._field = goocanvas.Canvas()
        self._field.set_size_request(400, 400)
        self._limits = limits # left, right, bottom, top
        self._objects = []
        self._w.add(self._field)
        self._w.show_all()
        self._root = root = self._field.get_root_item()
        self._rect = goocanvas.Rect(parent=self._root)
        self._on_screen_resize()
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
        left, bottom = self._limits[0], self._limits[2]
        return self._xf * (x - left), self._yf * (y - bottom)

    def _update(self, results):
        fill_color = 'black'
        radius = 3
        parent = self._root
        if len(self._objects) != len(results):
            self._objects = [goocanvas.Ellipse(parent = parent,
            center_x = 0, center_y = 0,
            radius_x = radius, radius_y = radius,
            fill_color = fill_color)
                for x, y, in results]
        for (res_x, res_y), obj in zip(results, self._objects):
            x, y = self.results_to_screen(res_x, res_y)
            obj.set_property('center-x', x)
            obj.set_property('center-y', y)

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
        if len(result) > len(self._lines):
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
        self._con = con
        self._con.registerToCamera().addCallback(self._finishInit)
        super(VideoWindow, self).__init__(tick_cb=self.getNew, dt=0.5)
        self._im = gtkim = gtk.Image()
        self._w.add(gtkim)
        self._w.show_all()

    def _finishInit(self):
        self._startTaskFirstTime()

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


