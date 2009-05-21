#!/usr/bin/python

"""
Shell for playing with Nao Robots through the Naoqi SOAP protocol using
a python only implementation.
"""

import sys, os, time
import optparse
import urllib2
from math import log10

# add path of burst library
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi
from burst_util import isnumeric, minimal_title, pairit

# we use twisted in a thread if requested
options = pynaoqi.getDefaultOptions()

if options.twisted:
    # Try to throw in gtk support
    from twisted.internet import gtk2reactor

    # we should be the first to install it, so no need for try/except
    gtk2reactor.install()

import gtk

has_matplotlib = False
try:
    import matplotlib
    has_matplotlib = True
except:
    pass

if has_matplotlib:
    matplotlib.use('GTK')

################################################################################
# Gui Widgets

from pynaoqi.widgets import (GtkTextLogger, GtkTimeTicker,
    CanvasTicker, VideoWindow)

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

def plottime(names, limits=(0.0, 320.0)):
    return GtkTimeTicker(lambda: con.ALMemory.getListData(names), limits=limits)

video_window = None
def video():
    global video_window
    if video_window is None:
        video_window = VideoWindow(con)

def canvaspairs(l, limits=[0,320,0,320]):
    return CanvasTicker(lambda: con.ALMemory.getListData(l).addCallback(pairit), limits=limits)

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
    my_ns['plottime'] = plottime
    my_ns['canvaspairs'] = canvaspairs
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
    globals()['con'] = con # <--- global connection object

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
        nicefloats = burst_util.nicefloats,
        pairit = burst_util.pairit,
        joints = Joints,
        )

    if options.twisted:
        main_twisted(con, my_ns)
    else:
        main_no_twisted(con, my_ns)


if __name__ == '__main__':
    main()

