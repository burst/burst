#!/usr/bin/python

"""
Shell for playing with Nao Robots through the Naoqi SOAP protocol using
a python only implementation.
"""

import sys, os, time
import glob
import optparse
import urllib2
from math import log10
import math

# add path of burst library
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi

# we use twisted in a thread if requested
options = pynaoqi.getDefaultOptions()

if options.twisted and not options.nogtk:
    print "DEBUG: USING GTK LOOP"
    # Try to throw in gtk support
    from twisted.internet import gtk2reactor

    try:
        gtk2reactor.install()
    except:
        pass

has_matplotlib = False
try:
    import matplotlib
    has_matplotlib = True
except:
    pass

if has_matplotlib and not options.nogtk:
    print "DEBUG: USING MATPLOTLIB WITH GTK"
    matplotlib.use('GTK')

def import_burst():
    # Fiasco: burst does it's own option parsing, which conflicts with IPython's
    # so we remove some stuff from the options arguments.. ugly, but works.
    old_argv = sys.argv
    sys.argv = sys.argv[:]
    bad_options = ['-pylab']
    for opt in bad_options:
        if opt in sys.argv:
            del sys.argv[sys.argv.index(opt)]
    import burst.moves as moves
    sys.argv = old_argv
    # End of fiasco

# IMPORTANT: this must happen after gtk2reactor, or bust.
import_burst()
import burst.moves as moves
from burst_util import isnumeric, minimal_title, pairit

from burst import field

################################################################################
# Gui Widgets

from pynaoqi.widgets import (GtkTextLogger, GtkTimeTicker,
    CanvasTicker, VideoWindow, PlottingWindow)

from pynaoqi.gui import Joints

def watch(names):
    """ watch multiple variables. For instance:
    l = refilter('Ball.*((dist)|(bearing))', names)
    watch(*l)
    """

    def prettyprint(results):
        return [(isnumeric(f) and '%3.3f' or '%s') % f for f in results]

    return GtkTextLogger(lambda:
        con.ALMemory.getListData(names).addCallback(prettyprint),
        title = '%s - %s' % (options.ip, minimal_title(names)))

def plottime(names, limits=(0.0, 320.0), dt=1.0):
    return GtkTimeTicker(lambda: con.ALMemory.getListData(names), limits=limits, dt=dt)

video_window = None
def video():
    global video_window
    if video_window is None:
        video_window = VideoWindow(con)

def canvaspairs(l, limits=[0,320,0,320], statics=None):
    from twisted.internet.defer import succeed
    # test case - will also work without a nao connection
    if l == []:
        return CanvasTicker(lambda: succeed([]), limits=limits, statics=statics)
    return CanvasTicker(lambda: con.ALMemory.getListData(l).addCallback(pairit), limits=limits, statics=statics)

def fieldpairs(l, limits=(-1000.0, 1000.0, -1000.0, 1000.0)):
    # Note - statics needs to be z sorted - lowest object
    # first, so rectangles go first, and green goes before white.
    return CanvasTicker(lambda: con.ALMemory.getListData(l).addCallback(pairit),
        limits=limits,
        statics=list(field.rects) + map(list, field.landmarks))

def fieldshow(callback=None, limits=field.green_limits):
    if callback is None:
        import burst.kinematics as kinematics
        callback = lambda: kinematics.pose.updateLocations(con)
    return CanvasTicker(callback, limits=limits,
        statics=list(field.rects) + map(list, field.landmarks))

class Data(object):

    def __init__(self, d):
        self.__dict__.update(d)
        self._d = d

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return repr(self._d)

from burst.consts import vision_vars
#vision = refilter('^/.*[cC]enter', names)
vision_vars_parts = [x.split('/')[3:] for x in vision_vars]

def format_vision_vars(v):
    d = {}
    for parts, val in zip(vision_vars_parts, v):
        k, k2 = parts[0], parts[1].lower() # make the data key lowercase
                                           # (focDist->focdist)
        recorded_k2 = {'dist':'distance', 'bearing':'bearingdeg'}.get(k2, k2)
        if k not in d:
            d[k] = {}
        d[k][recorded_k2] = val
    for k in d.keys():
        d[k] = Data(d[k])
    return Data(d)

def onevision(d=None):
    """ shortcut to get vision as a nice attribute laden class """
    if not d:
        d = con.ALMemory.getListData(vision_vars)
    return d.addCallback(format_vision_vars)

def get_list_of_players():
    import players
    return [x for x in [os.path.splitext(os.path.basename(x))[0]
        for x in glob.glob(os.path.dirname(players.__file__) + '/*.py')] if x[0] != '_']

def startplayer(name, clazz=None):
    """ Debugging from pynaoqi. Now that everything works with twisted, almost, we
    can use twisted to run previously naoqi only code, directly from pynaoqi shell.
    """
    import burst.player
    try:
        mod = __import__('players.%s' % name)
        playermod = getattr(mod, name)
    except:
        print "no such player"
        print "try one of:"
        print ', '.join(get_list_of_players())
        return
    candidate_classes = [v for v in playermod.__dict__.values()
                            if isinstance(v, type) and issubclass(v, burst.player.Player)
                            and not v is burst.player.Player]
    if len(candidate_classes) == 0:
        print "%s contains no Player classes" % playermod.__name__
        return None
    if len(candidate_classes) > 1:
        print "more then one Player in %s" % playermod.__name__
        if clazz is None:
            ctor = candidate_classes[0]
            print "taking the first out of %s" % candidate_classes
        else:
            if hasattr(playermod, clazz):
                ctor = getattr(playermod, clazz)
            else:
                print "no such class in %s" % playermod.__name__
                return None
    else:
        ctor = candidate_classes[0]
    print "Initializing player %s" % ctor.__class__.__name__
    # Finally, start the update task.
    import burst.eventmanager as eventmanager
    return eventmanager.TwistedMainLoop(ctor, control_reactor=False)

#############################################################################

EXAMPLES = """# Show current identified ball location
ball = refilter('^/.*Ball.*center', names)
con.ALMemory.getListData(ball)

# Vision Location of ball over time, in text, in plot
watch(ball)
plottime(ball)

# Vision positions on a canvas
vision = refilter('^/.*[cC]enter', names)
canvaspairs(vision)

# Battery in a plot
battery = refilter('Battery.*Value',names)
plottime(battery, limits=[-1.0,1.0])

# Localization positions for self and ball on canvas
loc = refilter('[XY]Est',names)
fieldpairs(loc)
fieldpairs(loc, limits=field.green_limits)
fieldpairs(loc, limits=field.white_limits)
fieldshow()

# Kinematics (import takes some time, hence not done by default)
import burst.kinematics as kin
kin.pose.update(con)

"""
def examples():
    print EXAMPLES

def f():
    return 42

def start_names_request(my_ns):
    # get the list of all variables - this can take a little
    # while on the robot, but it is async, so it should be fine
    def onDataListName(names):
        my_ns['names'] = names

    con.modulesDeferred.addCallback(
        lambda _:con.ALMemory.getDataListName().addCallback(onDataListName))

def make_shell_namespace(use_pylab):
    """
    Returns a namespace prepopulated with any variable we want in the global
    namespace for easy naoqi developing and debugging.
    """

    import burst_util
    import vision_definitions
    from twisted.internet import task
    from twisted.internet import defer

    def pr(x):
        print str(x)

    my_ns = dict(
        # globals
        task = task,
        succeed = defer.succeed,
        # pynaoqi
        con = con,
        pynaoqi = pynaoqi,
        joints = Joints,
        pr = pr,
        loop = GtkTextLogger,
        watch = watch,
        plottime = plottime,
        canvaspairs = canvaspairs,
        fieldpairs = fieldpairs,
        fieldshow = fieldshow,
        video = video,
        examples = examples,
        format_vision_vars = format_vision_vars,
        onevision = onevision,
        CanvasTicker = CanvasTicker,
        startplayer = startplayer,
        # burst
        moves = moves,
        field = field,
        vision_definitions = vision_definitions,
        refilter = burst_util.refilter,
        redir = burst_util.redir,
        nicefloats = burst_util.nicefloats,
        pairit = burst_util.pairit,
        # asaf
        f = f,
        # place holder until onDataListName works
        names = 'fetching..',
        )

    my_ns.update(math.__dict__)
    #my_ns.update(numpy.__dict__)
    if use_pylab:
        pylab = __import__('pylab')
        pylab.interactive(True)
        my_ns.update(pylab.__dict__)
        my_ns['pylab'] = pylab

    if not pynaoqi.options.nogtk:
        import gtk
        my_ns['gtk'] = gtk

    return my_ns

def twisted_banner(print_own_deferred_help):
    print "<"*30 + "o"*20 + ">"*30
    print """Pynaoqi shell - con object holds everything.
To generate help, call con.makeHelp()
To generate help on a single module, call con.ALMotion.makeHelp()"""
    if print_own_deferred_help:
        print """Deferreds: Any operation returning a deferred will return immediately
as expected, and additionally once its callback is called it will be
printed and available as _d."""

    print """
    Some Examples of usage:

""" + EXAMPLES + """
Use examples() to show this later.
"""
    print "_"*80

def main_twisted(con, my_ns):

    #from ipy import IPShellTwisted
    from IPython.twshell import IPShellTwisted

    tshell = IPShellTwisted(argv=[], user_ns=my_ns)
    shell = tshell.IP
    pimp_my_shell(shell, con)

    twisted_banner(print_own_deferred_help = True)

    # Start the mainloop, and add a hook to display deferred results when they
    # are available (also affects *any* deferred you try to print)
    import twisted.internet.defer as defer
    from IPython.hooks import result_display
    from IPython.genutils import Term

    def print_deferred(x):
        s = str(x)
        if len(s) > 1000:
            s = s[:1000] + '...'
        print >>Term.cout, "deferred: %s" % s
        shell.user_ns['_d'] = x
        return x

    def display_deferred(self, arg):
        # don't display already called deferreds?
        if isinstance(arg, defer.Deferred):
            arg.addCallback(print_deferred)
        else:
            result_display(self, arg)
    shell.set_hook('result_display', display_deferred)

    start_names_request(my_ns)

    tshell.mainloop()

def runWithProtocol(klass):
    import termios, tty
    from twisted.internet import reactor, stdio
    from twisted.conch.insults.insults import ServerProtocol

    fd = sys.__stdin__.fileno()
    oldSettings = termios.tcgetattr(fd)
    tty.setraw(fd)
    try:
        p = ServerProtocol(klass)
        stdio.StandardIO(p)
        reactor.run()
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, oldSettings)
        #os.write(fd, "\r\x1bc\r")

def main_twisted_manhole(con, my_ns):
    from twisted.conch.stdio import ConsoleManhole

    class PynaoqiConsole(ConsoleManhole):

        """ For reference see:
            twisted.conch.recvline.RecvLine

        TODO: don't reset screen when ^D is called (doesn't happen
        on raise SystemExit, but then an exception is unhandled)
        """

        def __init__(self):
            super(PynaoqiConsole, self).__init__(namespace = my_ns)
            self.updatePrompts()
            con.modulesDeferred.addCallback(self.updatePrompts)

        def updatePrompts(self):
            # RecvLine actually reads these
            self.ps = ("%s %s>>> " % (con.host, not con._modules and "NM " or ""), '... ')

        def connectionMade(self):
            super(PynaoqiConsole, self).connectionMade()
            start_names_request(self.namespace)

        def initializeScreen(self):
            # Override RecvLine
            self.terminal.write(self.ps[self.pn])
            self.setInsertMode()

    runWithProtocol(PynaoqiConsole)

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
    globals()['con'] = con # <--- global connection object

    my_ns = make_shell_namespace(use_pylab = '-pylab' in sys.argv)

    if options.twisted:
        if options.use_manhole:
            main_twisted_manhole(con, my_ns)
        else:
            main_twisted(con, my_ns)
    else:
        main_no_twisted(con, my_ns)


if __name__ == '__main__':
    main()

