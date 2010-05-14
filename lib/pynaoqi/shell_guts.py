import sys, os, time
import glob
import optparse
import urllib2
from math import log10
import math

from twisted.internet.defer import Deferred, succeed

# add path of burst library
burst_lib = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../lib'))
sys.path.append(burst_lib)

import pynaoqi

# we use twisted in a thread if requested
options = pynaoqi.getDefaultOptions()
con = pynaoqi.getDefaultConnection()

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
from burst_consts import YELLOW_GOAL, BLUE_GOAL
from burst import field

################################################################################
# Gui Widgets

def get_widgets():
    from widgets import (GtkTextLogger, GtkTimeTicker,
        CanvasTicker, VideoWindow, PlottingWindow, Calibrator, NotesWindow,
        GtkTextCompactingLogger)

    from gui import Joints

def watch(names, dt=1.0):
    """ watch multiple variables. For instance:
    l = refilter('Ball.*((dist)|(bearing))', names)
    watch(*l)
    """

    def prettyprint(results):
        return [(isnumeric(f) and '%3.3f' or '%s') % f for f in results]

    return GtkTextLogger(lambda:
        con.ALMemory.getListData(names).addCallback(prettyprint),
        title = '%s - %s' % (options.ip, minimal_title(names)), dt=dt)

def plottime(names, limits=(0.0, 320.0), dt=1.0):
    from widgets import GtkTimeTicker
    return GtkTimeTicker(lambda: con.ALMemory.getListData(names), limits=limits, dt=dt)

##### Allow for a single video window to be open ########
video_window = None
def _onVideoClose(window):
    global video_window
    video_window = None

def one_window(name, ctor):
    glob = globals()
    def onClose(window):
        globals()[name] = None
    if not name in glob or glob[name] is None:
        obj = glob[name] = ctor()
        obj.onClose.addCallback(onClose)
    return glob[name]

video = lambda dt=0.5: one_window('video_window', lambda: VideoWindow(con=con, dt=dt))
calibrator = lambda: one_window('calibrator_window', lambda: Calibrator(con))
notes = lambda: one_window('notes_window', lambda: NotesWindow(con))

#########################################################

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
        import burst.world.kinematics as kinematics
        callback = lambda: kinematics.pose.updateLocations(con)
    return CanvasTicker(callback, limits=limits,
        statics=list(field.rects) + map(list, field.landmarks))

################################################################################
# Remote control through remote_control supervisor
# see webots/controllers/remote_control/remote_control.py
RC_PORT = 13434
WEBOTS_STANDING_Z = 0.32195
WEBOTS_BALL_Z = 0.0428038
# TODO - put in burst_consts.
webots_goal_dist_from_center = 3.11 * 1.07 #3.3277
burst_field_width = 605.0 # cm
k = webots_goal_dist_from_center / (burst_field_width / 2)
konv = 1.0 / k
WORLD_STANDING_Z = WEBOTS_STANDING_Z * konv
WORLD_BALL_Z = WEBOTS_BALL_Z * konv

class RemoteControl(object):
    def __init__(self):
        self.s = None
    def tryConnect(self):
        if self.s is None:
            import socket
            self.s = socket.socket()
        if not self.connected():
            try:
                self.s.connect(('127.0.0.1', RC_PORT))
            except:
                return False
        return self.connected()
    def connected(self):
        #return self.s.getsockname()[0] == '0.0.0.0'
        if self.s is None: return False
        try:
            self.s.getpeername()
            return True
        except:
            return False
    def send(self, line):
        if not self.tryConnect():
            print "no one home"
            return
        if len(line) == 0 or line[-1] != '\n': line = line + '\n'
        self.s.send(line)
    def origin(self):
        self.pos(0, 0, WEBOTS_STANDING_Z)
    def rotblue(self):
        self.send('rotblue')
    def rotyellow(self):
        self.send('rotyellow')
    def pos(self, x, y, z=WORLD_STANDING_Z):
        # bug in current pos of remote_control.py - zero should be our goal, not midpoint.
        self.send('pos %s %s %s' % (-x+field.MIDFIELD_X, y, max(WORLD_STANDING_Z, z)))
    def ball(self, x, y):
        self.send('ball %s %s %s' % (x, y, WORLD_BALL_Z))
    def rot(self, x, y, z, alpha):
        self.send('rot %s %s %s %s' % (x, y, z, alpha))
    def player_name(self, name):
        self.send('player_name %s' % name)

def headup(con):
    return con.ALMotion.setAngle('HeadPitch', -0.6)

remote = RemoteControl()

################################################################################
# Vision Helpers

class Data(object):

    def __init__(self, d):
        self.__dict__.update(d)
        self._d = d

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return repr(self._d)

from burst_consts import vision_vars
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

################################################################################
# Support for Debugging Players from within pynaoqi

def get_submodules(basemod):
    return [x for x in [os.path.splitext(os.path.basename(x))[0]
        for x in glob.glob(os.path.dirname(basemod.__file__) + '/*.py')] if x[0] != '_']

def get_list_of_players():
    import players
    return get_submodules(players)

def get_list_of_tests():
    import players.tests
    return get_submodules(players.tests)

class PlayerRunner(object):

    def __init__(self, players, fullname):
        self.fullname = fullname
        self._players = players
        self._player = None
        self._main = None

    def make(self):
        import shell
        user_ns = shell.user_ns
        self.loop = makeplayerloop(self.fullname)
        self._players.last = self.loop
        if hasattr(self.loop, '_player'): # why? network problems?
            user_ns['player'] = self._player = self.loop._player
            user_ns['main'] = self._main = self.loop._player._main_behavior
            user_ns['world'] = self._main._world
            user_ns['actions'] = self._main._actions._actions
            user_ns['eventmanager'] = self._main._eventmanager._eventmanager
            for k in ['searcher', 'centerer', 'localizer', 'tracker']:
                user_ns[k] = getattr(self._main._actions._actions, k)
            for k in ['ball', 'our_goal', 'opposing_goal', 'our_lp', 'our_rp',
                'opposing_lp', 'opposing_rp']:
                user_ns[k] = getattr(self._main._world, k)
            user_ns['our_unknown'] = self._main._world.our_goal.unknown
            user_ns['opposing_unknown'] = self._main._world.opposing_goal.unknown

    def switch_color(self):
        # TODO - simulate chest button (change the AL_MEMORY var?)
        if not self._player: return
        self._main._world.playerSettings.toggleteamColor()
        print str(self._main._world.playerSettings)

    def start(self):
        try:
            import widgets
        except:
            pass
        else:
            for l in widgets.TaskBaseWindow.loggers:
                l.appendLine('> %s started <' % self.fullname)
        self.make()
        self.loop.start()
        return self._main # to allow onDone for stoppage of behavior

    def stop(self):
        def log_stop():
            try:
                import widgets
            except:
                pass
            else:
                for l in widgets.TaskBaseWindow.loggers:
                    l.appendLine('> %s stopped <' % self.fullname)
        bd = self._main.stop()
        bd.onDone(self.loop.shutdown).onDone(log_stop)
        return bd

class Players(object):
    """ Used by pynaoqi shell to let completion work it's magic
    """
    def __init__(self, thelist):
        self.players_list = list(thelist)
        self.runners = []
        for player in self.players_list:
            name = player.rsplit('.',1)[-1]
            self.__dict__[name] = runner = PlayerRunner(self, player)
            self.runners.append((name, runner))

def getInitialBehavior(module_name, verbose=True):
    import burst.behavior
    base, last = module_name.rsplit('.', 1)
    try:
        playermod = __import__(module_name, fromlist=[''])
    except SyntaxError, e:
        raise # Ipython catches, clear win.
    except ImportError:
        if verbose:
            print "no such player"
            print "try one of:"
            print ', '.join(players.players_list)
        return None
    candidate_classes = [v for v in playermod.__dict__.values()
                            if isinstance(v, type) and issubclass(v, burst.behavior.InitialBehavior)
                            and not v is burst.behavior.InitialBehavior]
    if len(candidate_classes) == 0:
        if verbose:
            print "%s contains no InitialBehavior classes" % playermod.__name__
        return None
    if len(candidate_classes) > 1:
        print "more then one InitialBehavior in %s" % playermod.__name__
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
    return ctor


# Keep lists of players and tests for easy running.
import players as players_mod
import players.tests as tests_mod
players_modules = ['players.%s' % x for x in get_submodules(players_mod)]
tests_modules = ['players.tests.%s' % x for x in get_submodules(tests_mod)]
players = Players(players_modules)
tests = Players(tests_modules)

class BehaviorsContainer(object):
    def __init__(self):
        behaviors = [x for x in [getInitialBehavior(x, verbose=False)
                       for x in players_modules + tests_modules] if x is not None]
        for b in behaviors:
            setattr(self, b.__name__, b)
behaviors = BehaviorsContainer()

def makeplayerloop(module_name, clazz=None):
    """ Debugging from pynaoqi. Now that everything works with twisted, almost, we
    can use twisted to run previously naoqi only code, directly from pynaoqi shell.
    """
    ctor = getInitialBehavior(module_name)
    if ctor is None:
        import pdb; pdb.set_trace()
    print "Initializing player %s" % ctor.__name__
    # Finally, start the update task.
    import burst.eventmanager as eventmanager
    loop = eventmanager.TwistedMainLoop(ctor, reactor=False, startRightNow=False)
    loop.initMainObjectsAndPlayer()
    return loop

from burst.eventmanager import ExternalMainLoop

def beone(b, goal):
    eml = ExternalMainLoop(b)
    # Doesn't work - configure is recalled by the Player.
    #eml._world.configure(goal)
    return eml

beblue = lambda b: beone(b, BLUE_GOAL)
beyellow = lambda b: beone(b, YELLOW_GOAL)

################################################################################

def fps(c, dt):
    first=c()
    while True:
        cur=c()
        yield((cur-first)/dt)
        first = cur

f=fps(lambda: user_ns['eventmanager'].frame, 1.0)
fps = lambda: checking_loop(lambda: f.next())

def checking_loop(f, widget=None, **kw):
    if widget is None:
        import widgets
        widget = widgets.GtkTextLogger
    first = f()
    if isinstance(first, Deferred):
        widget(f, **kw)
    else:
        widget(lambda: succeed(f()), **kw)

compacting_loop = lambda f: checking_loop(f, widget=GtkTextCompactingLogger, dt=0.1)


