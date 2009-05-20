#!/usr/bin/python

"""
Shell for playing with Nao Robots through the Naoqi SOAP protocol using
a python only implementation.
"""

import sys, os, time
import optparse
import urllib2

# add path of burst library
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi
from burst_util import isnumeric, minimal_title

# we use twisted in a thread if requested
options = pynaoqi.getDefaultOptions()

if options.twisted:
    # Try to throw in gtk support
    from twisted.internet import gtk2reactor

    # we should be the first to install it, so no need for try/except
    gtk2reactor.install()

import gtk

#############################################################################

class BaseWindow(object):

    counter = 1

    def __init__(self):
        self._title = 'base'
        self._w = w = gtk.Window()
        w.connect("delete-event", self._onDestroy)

    def _onDestroy(self, target, event):
        print "stopping task"
        self.stop()
        self._w.destroy()

    def show(self):
        self._w.show()

    def hide(self):
        self._w.hide()


class TaskBaseWindow(BaseWindow):

    def __init__(self, tick_cb, dt=1.0):
        super(TaskBaseWindow, self).__init__()
        from twisted.internet import task
        self._dt = dt
        self._tick_cb = tick_cb
        self._task = task.LoopingCall(self._onLoop)

    def _startTaskFirstTime(self):
        self._start = time.time()
        self.start()

    def stop(self):
        if self._task.running:
            self._task.stop()

    def start(self):
        if not self._task.running:
            self._task.start(self._dt)

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
    counter = 1
    loggers = []

    """
    @tick_cb - function that returns the value to display, preferably
    as a string. (if not str is called on it). Will be called repeatedly.
    @dt - time between calls.
    @title - title of window.
    """
    def __init__(self, tick_cb, title=None, dt=1.0):
        super(GtkTextLogger, self).__init__(tick_cb=tick_cb, dt=dt)
        if title is None:
            title = '%s %s' % (options.ip, self.counter)
        self._title = title
        self.counter += 1
        self._tv = tv = gtk.TextView()
        self._tb = tb = gtk.TextBuffer()
        self._sw = gtk.ScrolledWindow()
        self._sw.add(self._tv)
        self._w.add(self._sw)
        self._w.set_size_request(300,300)
        self._w.show_all()
        tv.set_buffer(tb)
        self._startTaskFirstTime()
        self.loggers.append(self)

    # Task Methods

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

    def stop(self):
        super(GtkTextLogger, self).stop()
        self.set_title()

    def start(self):
        super(GtkTextLogger, self).start()
        self.set_title()

    # GUI Methods
    def set_title(self, txt=None):
        if txt is None:
            txt = self._title
        self._w.set_title('%s - %s' % (
            self._task.running and 'running' or 'stopped', txt))
        self._title = txt

    # Internal Methods

    def _onDestroy(self, target, event):
        print "stopping task"
        self.stop()
        super(GtkTextLogger, self)._onDestroy(target, event)

    def _update(self, result):
        #if not self._w.is_active(): return
        tb = self._tb
        tb.insert(tb.get_start_iter(), '%3.3f: %s\n' % (
            (time.time() - self._start), str(result)))

class VideoWindow(TaskBaseWindow):

    def __init__(self, con):
        self._con = con
        self._con.registerToCamera()
        super(VideoWindow, self).__init__(tick_cb=self.getNew, dt=0.5)
        import twisted.internet.task as task
        self._im = gtkim = gtk.Image()
        self._w.add(gtkim)
        self._w.show_all()
        self._startTaskFirstTime()

    def getNew(self):
        #import pdb; pdb.set_trace()
        return self._con.getRGBRemoteFromYUV422()

    def _update(self, result):
        width, height, rgb = result
        pixbuf = gtk.gdk.pixbuf_new_from_data(rgb, gtk.gdk.COLORSPACE_RGB, False, 8, width, height, width*3)
        self._im.set_from_pixbuf(pixbuf)

def watch(*names):
    """ watch multiple variables. For instance:
    l = refilter('Ball.*((dist)|(bearing))', names)
    watch(*l)
    """

    def prettyprint(results):
        return [(isnumeric(f) and '%3.3f' or '%s') % f for f in results]

    GtkTextLogger(lambda:
        con.ALMemory.getListData(names).addCallback(prettyprint),
        title = '%s - %s' % (options.ip, minimal_title(names)))

video_window = None
def video():
    global video_window
    if video_window is None:
        video_window = VideoWindow(con)

#############################################################################

def main_twisted(con, my_ns):

    from ipy import IPShellTwisted

    tshell = IPShellTwisted(argv=[], user_ns=my_ns)
    shell = tshell.IP
    pimp_my_shell(shell, con)

    print "<"*30 + "o"*20 + ">"*30
    print """Pynaoqi shell - con object holds everything.
To generate help, call con.makeHelp()
To generate help on a single module, call con.ALMotion.makeHelp()"""
    print """Deferreds: Any operation returning a deferred will return immediately
as expected, and additionally once its callback is called it will be
printed and available as _d."""
    print "_"*80

    from twisted.internet import task
    import gtk

    def pr(x):
        print str(x)

    my_ns['gtk'] = gtk
    my_ns['task'] = task
    my_ns['pr'] = pr
    my_ns['loop'] = GtkTextLogger
    my_ns['watch'] = watch
    my_ns['video'] = video
    # place holder until onDataListName works
    my_ns['names'] = 'fetching..'

    # Start the mainloop, and add a hook to display deferred results when they
    # are available (also affects *any* deferred you try to print)
    import twisted.internet.defer as defer
    from IPython.hooks import result_display
    from IPython.genutils import Term

    # get the list of all variables - this can take a little
    # while on the robot, but it is async, so it should be fine
    def onDataListName(names):
        shell.user_ns['names'] = names

    con.modulesDeferred.addCallback(
        lambda _:con.ALMemory.getDataListName().addCallback(onDataListName))

    def pr(x):
        s = str(x)
        if len(s) > 1000:
            s = s[:1000] + '...'
        print >>Term.cout, "deferred: %s" % s
        shell.user_ns['_d'] = x
        return x

    def display_defer(self, arg):
        # don't display already called deferreds?
        if isinstance(arg, defer.Deferred):
            arg.addCallback(pr)
        else:
            result_display(self, arg)
    shell.set_hook('result_display', display_defer)
    tshell.mainloop()

#############################################################################

def main_no_twisted(con, my_ns):
    import IPython.ipapi
    shell = IPython.ipapi.launch_new_instance(my_ns)
    print "<"*30 + "o"*20 + ">"*30
    print """Pynaoqi shell - con object holds everything.
    To generate help, call con.makeHelp()
    To generate help on a single module, call con.ALMotion.makeHelp()
    """
    print "_"*80
    pimp_my_shell(shell, con)

#############################################################################

def pimp_my_shell(shell, con):
    # set a nicer prompt to tell the user where he is connected to
    # reminder: can use ${} to eval stuff, like: '${con.host} [\#]: '
    # NM stands for No Modules
    shell.outputcache.prompt1.p_template='%s ${not con._modules and "NM " or ""}[\#]: ' % (con.host)

#############################################################################

def main():
    # If you are looking for command line parsing, it happens
    # in pynaoqi.getDefaultConnection (actually in pynaoqi.getDefaultOptions)
    try:
        con = pynaoqi.getDefaultConnection()
    except urllib2.URLError, e:
        print "error connecting: %s" % e
        raise SystemExit

    import burst.moves as moves
    import burst_util
    import vision_definitions

    my_ns = dict(
        con = con,
        pynaoqi = pynaoqi,
        moves = moves,
        vision_definitions = vision_definitions,
        refilter = burst_util.refilter,
        redir = burst_util.redir,
        nicefloats = burst_util.nicefloats)

    if options.twisted:
        main_twisted(con, my_ns)
    else:
        main_no_twisted(con, my_ns)


if __name__ == '__main__':
    main()

