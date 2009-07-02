#!/usr/bin/python
"""
Shell for playing with Nao Robots through the Naoqi SOAP protocol using
a python only implementation.
"""

import sys

#############################################################################

EXAMPLES = [
('main',
"""
# run the joints controller
naojoints()
# show all events
compact(lambda: list(world.seenObjects()))
#loop(lambda: succeed(player._world._events), dt=0.1)
# in nicer form (also looks at eventmanager and not world - same thing I think)
#compact(lambda: map(burst_events.event_name, main._eventmanager._pending_events))
compact(lambda: map(burst_events.short_event_name, list(player._world._events)))
compact(lambda: [localizer.stopped, searcher.stopped, tracker.stopped, centerer.stopped])
compact(lambda: nicefloats([world.robot.world_x, world.robot.world_y, world.robot.world_heading]))
compact(lambda: str(opposing_goal.left)+str(opposing_goal.right))
tracker.verbose=not tracker.verbose
searcher.verbose=not searcher.verbose
localizer.verbose=not localizer.verbose
""")
,('centerer',
"""
centerer.start(target=world.ball)
centerer.start(target=list(world.seenObjects)[0])
centerer.start(target=world.seen_goal.left)
centerer.start(target=world.seen_goal.right)
"""
)
,
('remote',
"""
remote.rot(0,1,0,-0.5)
remote.ball(-300,0)
remote.pos(300,0,0)
remote.rotyellow()
remote.rotblue()
remote.player_name('BLUE_PLAYER_1')
remote.player_name('BLUE_GOAL_KEEPER')
remote.player_name('RED_GOAL_KEEPER')
remote.ball(-100,0)
remote.ball(100,0)
remote.origin()
remote.pos(0,100,0)
remote.pos(0,-100,0)
remote.pos(100,0,0)
remote.pos(-100,0,0)
"""
),
('events',
"""
# show all events
players.template_player.start()
loop(lambda: succeed(player._world._events), dt=0.1)
# in nicer form (also looks at eventmanager and not world - same thing I think)
loop(lambda: succeed(map(burst_events.event_name, main._eventmanager._pending_events)), dt=0.1)
""")
,
('pynaoqi',
"""
#!Pynaoqi
# you can have 
con.ALMemory.getListData(ball)
""")
,
('ball',
"""
# Show current identified ball location
#ball = refilter('^/.*Ball.*Center', names) # just CenterX/Y
ball = refilter('^/.*Ball.*(ear|ist|enter)', names) # More
watch(ball) # display ball variables
# Log the distance and focdistance (you need to run with -pylab)
# pynaoqi --ip raul -pylab
logger = watch(ball)
# wait a little
t, dist, focdist = logger._times, array(logger._values)[:,3], array(logger._values)[:,4]
plot(t, dist, t, focdist)
# Vision Location of ball over time, in text, in plot
watch(ball)
plottime(ball)
""")
,
('video',
"""
# Watch the thresholded image
v=video(dt=0.1)
v=video()
v.threshold()
# display a single image (need to run with -pylab)
a=frombuffer(v._thresholded,dtype=uint8).reshape((240,320))
imshow(a)
""")
, ('vision',
"""
# Vision positions on a canvas
vision = refilter('^/.*Center', names)
yellow=refilter('^/.*YG.P.*(Center|IDC)',names)
blue=refilter('^/.*BG.P.*(Center|IDC)',names)
canvaspairs(vision)
""")
,
('sensors',
"""
# Getting US Sensors
# subscribe first
con.ALSonar.subscribe("test", [500])
# note - the third one is strange. Once you use it, the Actuator shows 3 (0 before), and the values are different then
# those you get from the Sensor.
watch(["Device/SubDeviceList/US/Sensor/Value", "Device/SubDeviceList/US/Actuator/Value", 'extractors/alsonar/distances'])

# Battery in a plot
battery = refilter('Battery.*Value',names)
plottime(battery, limits=[-1.0,1.0])
""")
,
('localization',
"""
# Localization positions for self and ball on canvas
loc = refilter('[XY]Est',names)
fieldpairs(loc)
fieldpairs(loc, limits=field.green_limits)
fieldpairs(loc, limits=field.white_limits)
fieldshow()

# Kinematics (import takes some time, hence not done by default)
import burst.kinematics as kin
kin.pose.update(con)
# Watch distance estimates to field goal posts
loop(lambda: kin.pose.update(con).addCallback(lambda _: (kin.pose._estimates['YGLP'][0][0], kin.pose._estimates['YGRP'][0][0])))
""")
,
('other',
"""
# Running a player (BROKEN)
players.localize.start()
players.localize.stop()
players.localize.init() # for inspecting, doesn't start, just constructs

# See the Nack/Ack bug
bug=refilter('ChestBoard/[NA][ac]',names)
watch(bug)
""")
,
('debugging',
"""
# Localization debugging, a bunch of variables. Not strange, just ugly.
loop(lambda: kin.pose.update(con).addCallback(lambda _: nicefloats([kin.pose._estimates['YGLP'][0][0], kin.pose._estimates['YGRP'][0][0]] + kin.pose.cameraToWorldFrame[0].tolist() + kin.pose._bodyAngles[:2] + [kin.pose._v.YGRP.height+kin.pose._v.YGRP.y, kin.pose._v.YGRP.x, kin.pose._v.YGLP.height+kin.pose._v.YGLP.y, kin.pose._v.YGLP.x+kin.pose._v.YGLP.width])))

# Network status

# Show number of connections and number of packets over time
loop(lambda: succeed((len(con.connection_manager._protocols), sum(p._packets for p in con.connection_manager._protocols))))

# Show number of packets per connection
loop(lambda: succeed([x._packets for x in con.connection_manager._protocols]))
""")
,
('more_tests',
"""
# test burstmem
con.burstmem.getNumberOfVariables()
# that says "120" after a sec (depends)
r=[con.burstmem.getVarNameByIndex(i) for i in xrange(120)]
# wait slightly
r=[x.result for x in r]
""")
]

def examples():
    print """
    Some Examples of usage:

""" + '\n'.join(['%s:\n%s' % (k,v) for k, v in EXAMPLES]) + """
Use examples() to show this later.
"""
    print "_"*80

def start_names_request(my_ns):
    # get the list of all variables - this can take a little
    # while on the robot, but it is async, so it should be fine
    def onDataListName(names):
        my_ns['names'] = names

    con.modulesDeferred.addCallback(
        lambda _:con.ALMemory.getDataListName().addCallback(onDataListName))

def make_shell_namespace(use_pylab, using_gtk, con):
    """
    Returns a namespace prepopulated with any variable we want in the global
    namespace for easy naoqi developing and debugging.
    """
    import pynaoqi
    import math
    from shell_guts import (format_vision_vars, onevision, makeplayerloop,
        players, tests, moves, field, f, fps, behaviors,
        checking_loop, compacting_loop, watch, plottime, canvaspairs,
        fieldpairs, fieldshow, video, calibrator, notes, remote,
        beblue, beyellow, headup)
    from burst.eventmanager import ExternalMainLoop
    from . import testers

    import burst
    from gui import Joints
    from widgets import CanvasTicker
    import burst_util
    import burst_consts as consts
    import burst_events
    import burst.image as image
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
        pr = pr,
        examples = examples,
        format_vision_vars = format_vision_vars,
        onevision = onevision,
        makeplayerloop = makeplayerloop,
        players = players,
        behaviors = behaviors,
        tests = tests,
        player = None, # set by players.bla.start()
        remote = remote,
        testers = testers,
        # burst
        burst = burst,
        burst_util = burst_util,
        moves = moves,
        field = field,
        consts = consts,
        burst_consts = consts,
        burst_events = burst_events,
        vision_definitions = vision_definitions,
        image = image,
        ExternalMainLoop = ExternalMainLoop,
        beblue = beblue,
        beyellow = beyellow,
        # utilities
        refilter = burst_util.refilter,
        redir = burst_util.redir,
        nicefloats = burst_util.nicefloats,
        pairit = burst_util.pairit,
        headup = lambda con=con: headup(con),
        # asaf
        f = f,
        # place holder until onDataListName works
        names = 'fetching..',
        )

    if using_gtk:
        import gtk
        my_ns.update(dict(
            naojoints = Joints,
            fps = fps,
            loop = checking_loop,
            compact = compacting_loop,
            watch = watch,
            plottime = plottime,
            canvaspairs = canvaspairs,
            fieldpairs = fieldpairs,
            fieldshow = fieldshow,
            video = video,
            calibrator = calibrator,
            notes = notes,
            CanvasTicker = CanvasTicker,
            gtk = gtk,
        ))

    my_ns.update(math.__dict__)
    #my_ns.update(numpy.__dict__)
    if use_pylab:
        pylab = __import__('pylab')
        pylab.interactive(True)
        my_ns.update(pylab.__dict__)
        my_ns['pylab'] = pylab

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
    
    import pynaoqi
    options = pynaoqi.getDefaultOptions()
    if options.examples:
        examples()

def main_twisted(con, my_ns):

    #from ipy import IPShellTwisted
    from IPython.twshell import IPShellTwisted

    tshell = IPShellTwisted(argv=[], user_ns=my_ns)
    shell = tshell.IP
    globals()['shell'] = shell # for later updating variables in user table
    globals()['user_ns'] = my_ns
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

def installgtkreactor():
    import pynaoqi
    options = pynaoqi.getDefaultOptions()
    if options.twisted:
        # Try to throw in gtk support
        using_gtk = False
        try:
            from twisted.internet import gtk2reactor
            gtk2reactor.install()
            using_gtk = True
        except AssertionError, e:
            using_gtk = True
        except:
            pass
        if using_gtk:
            print "DEBUG: USING GTK LOOP"
    return using_gtk

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
    installgtkreactor()
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
    using_gtk = installgtkreactor()
    # If you are looking for command line parsing, it happens
    # in pynaoqi.getDefaultConnection (actually in pynaoqi.getDefaultOptions)
    import urllib2
    import pynaoqi
    options = pynaoqi.getDefaultOptions()
    try:
        con = pynaoqi.getDefaultConnection()
    except urllib2.URLError, e:
        print "error connecting: %s" % e
        raise SystemExit
    globals()['con'] = con # <--- global connection object

    my_ns = make_shell_namespace(use_pylab = '-pylab' in sys.argv, using_gtk=using_gtk, con=con)

    if options.twisted:
        if options.use_manhole:
            main_twisted_manhole(con, my_ns)
        else:
            main_twisted(con, my_ns)
    else:
        main_no_twisted(con, my_ns)


if __name__ == '__main__':
    main()

