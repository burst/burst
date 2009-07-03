# controller for the simulation
from time import sleep
from math import atan2
import cPickle

import burst_consts

from shell_guts import remote
from . import getDefaultConnection

con = getDefaultConnection()

def step(eml):
    # bug in out main loop - requires two steps to be sure it got the image correctly (not sure actually where the bug is)
    for x in xrange(4):
        eml.doSingleStep()

def straight((a, b), (c, d), parts):
    """ generator for points linearily along line between (a, b) and (c, d)
    """
    assert(parts > 0)
    f_parts = float(parts)
    parts = int(parts)
    dx = (c - a) / f_parts
    dy = (d - b) / f_parts
    for i in xrange(parts):
        x, y = a + dx*i, b + dy*i
        print x, y
        yield x, y
    yield x, y

DT_SETTLE_DOWN = 0.5 # 2.0 on Roy's computer
DT_STEP = 0.1 * DT_SETTLE_DOWN

def goalposts(eml, count=5):
    """ eml - main loop object """

    # Walk the robot through a route, and record the seen bearing of both posts.
    # can then test various ways of computing them (using uncertain posts, etc.)

    con.ALMotion.setAngle('HeadPitch', -0.4)
    eml._world.configure(burst_consts.YELLOW_GOAL)
    sleep(0.5)

    loc = []
    posts = list(eml._world.opposing_goal.bottom_top) + list(eml._world.our_goal.bottom_top)


    # The world_x, world_y is not actually this, but we are turned (this depends on the goal or
    # something)

    #real_posts_xy = [
    #(0.0, 75.0),
    #(0.0, -75.0),
    #(605.0, 75.0),
    #(605.0, -75.0),
    #]
    real_posts_xy = [(p.world_x, p.world_y) for p in posts]

    def getdata(x, y):
        step(eml)
        def real_bearing(px, py):
            #print px, py, x, y, py - y,
            return atan2(py - y, px - x)
        return [(p.seen, p.update_time, p.bearing, p.dist, p.centerX, p.centerY, real_bearing(*real_pos)) for p, real_pos in zip(posts, real_posts_xy)]

    from burst_util import chainDeferreds

    def single(pos, loc):
        remote.pos(*pos)
        remote.rotblue()

    from twisted.internet import reactor

    for i, pos in enumerate(straight((100.0, -50.0), (550.0, -50.0), count)):
         reactor.callLater(i*DT_SETTLE_DOWN, single, pos,loc)
         reactor.callLater((i+1)*DT_SETTLE_DOWN - DT_STEP, lambda pos=pos, loc=loc: loc.append(getdata(*pos)))
    return loc

"""
You can do:
d,eml=testers.testGoalPosts()
# wait 22 seconds (d is a deferred result)
logs = d.result
testers.getBearingCenterXCenterYRealBearing(logs)

"""

def testGoalPosts(count=10):
    """ a,eml=testers.testGoalPosts() """
    from shell_guts import behaviors
    from burst.eventmanager import ExternalMainLoop
    eml = ExternalMainLoop(behaviors.NoInit)
    from twisted.internet import reactor
    from twisted.internet.defer import Deferred
    # NOTE: This is only filled in 20 seconds time
    d = Deferred()
    def doit(eml, count):
        logs = goalposts(eml, count)
        reactor.callLater((count+1)*DT_SETTLE_DOWN, d.callback, logs)
    reactor.callLater(2.0, doit, eml, count)
    return d, eml

def getBearingCenterXCenterYRealBearing(a):
    return [[(y[2], y[-3:]) for y in x if y[0]] for x in a]

filename = 'data.pickle'
def getPickle():
    if os.path.exists(filename):
        f1 = open(filename, 'r')
        d = cPickle.load(f1)
        f1.close()
    else:
        d = []
    f = open(file, 'w+')
    return f, d

def record(f, data):
    cPickle.dump(data, f)

