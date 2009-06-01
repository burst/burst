from __future__ import with_statement

import os
import sys
import re
from time import time
from math import cos, sin, sqrt, atan2
import linecache
import glob

# Data Structures

class RingBuffer(list):
    """ Todo - a more efficient implementation. (only
    if this becomes an issue)
    """
    def __init__(self, size):
        super(RingBuffer, self).__init__([None]*size)

    def ring_append(self, x):
        self.pop(0)
        self.append(x)

# Twisted-like Deferred and succeed

def returnSucceed(f):
    def wrapper(*args, **kw):
        return succeed(f(*args, **kw))
    return wrapper

class WrapWithDeferreds(object):

    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, k):
        # hack for 'post'
        target = getattr(getattr(self, '_obj'), k)
        if k == 'post':
            return WrapWithDeferreds(target)
        return returnSucceed(target)

class MyDeferred(object):
    """ mimic in the most minimal way twisted.internet.defer.Deferred """
    def __init__(self):
        self._callbacks = []
        self.called = 0
        # not setting self.result to mimic bug/feature in original

    def addCallback(self, f):
        """ Record or Apply a callback to the result.
        Two paths:
        self.called: apply f to existing result, update it in place
        else       : append f to self.callbacks

        both cases : return self
        """
        if self.called: # call immediately
            self.result = f(self.result) # saved for filter effect
        else:
            self._callbacks.append((f,None))
        return self

    def addErrback(self, f):
        if self.called:
            return
        else:
            self._callbacks.append((None, f))

    def callback(self, result):
        self.called = True
        self.result = result
        last_success = True
        handled = False
        for cb, eb in self._callbacks:
            if last_success:
                try:
                    self.result = cb(self.result)
                except Exception, e:
                    print "deferred problem %s" % str(e)
                    last_success = False
                    handled = False
            else:
                try:
                    self.result = eb(e)
                except Exception, e:
                    pass
                else:
                    handled = True
        if not last_success and not handled:
            # My fallback for when an errback hasn't been called,
            # but an exception has been raised.
            print "Unhandled Exception on deferred: %s" % str(e)
            import pdb; pdb.set_trace()

def succeed(result):
    d = Deferred()
    d.callback(result)
    return d

# These functions are just plain copied from twisted - should work with my simplified Deferred too
#/usr/local/lib/python2.6/dist-packages/Twisted-8.2.0-py2.6-linux-x86_64.egg/twisted/internet/defer.py

class MyDeferredList(MyDeferred):
    """ Very slim compared to the original. Minuses:
    doesn't handle errback (nor does my Deferred implementation)
    """

    def __init__(self, deferreds):
        super(MyDeferredList, self).__init__()
        self._deferreds = deferreds
        self._count = len(deferreds)
        # like twisted.internet.defer, collect pairs of (success, result),
        # only here it is always (True, result)
        self._results = [None for i in xrange(len(deferreds))]
        for i, d in enumerate(self._deferreds):
            d.addCallback(lambda result, i=i: self._onOne(result, i))

    def _onOne(self, result, i):
        self._count -= 1
        self._results[i] = (True, result)
        if self._count <= 0:
            self.callback(self._results)

def wrapDeferredWithBurstDeferred(d):
    """ call with no parameters - the only use case so far """
    bd = BurstDeferred(None)
    d.addCallback(lambda result: bd.callOnDone())
    return bd

try:
    # use the real thing if it is there
    from twisted.internet.defer import Deferred, DeferredList
except:
    Deferred = MyDeferred
    DeferredList = MyDeferredList

def chainDeferreds(deferred_makers):
    current = [0]
    dlast = Deferred()

    def _step(result):
        d = deferred_makers[current[0]](result)
        current[0] += 1
        if current[0] >= len(deferred_makers):
            d.addCallback(dlast.callback)
        else:
            d.addCallback(_step)

    _step(None)
    return dlast

# Slightly less twisted like chain geared deferred implementation

# TODO: Rename me
class BurstDeferred(object):
    """
    Normal Help:

        A Deferred is a promise to call you when some operation is complete.
    It is also concatenatable. What that means for implementation, is that
    when the operation is done we need to call a deferred we stored and gave
    the user when he gave us a callback. That deferred 

    Twisted users:

        Sort of like Deferred, only geared towards chainable deferreds, which
    is the only use case right now.  So basically you are expected to
    return from onDone a new BurstDeferred that will be called when the
    argument of onDone actually finishes.
    """

    def __init__(self, data, parent=None):
        self._data = data
        self._ondone = None
        self._completed = False # we need this for concatenation to work
        self._parent = parent # DEBUG only
    
    def onDone(self, cb):
        """ store a callback to be called when a result is complete.
        If it is already complete then it will be called right away. 
        """
        if cb is None:
            raise Exception("onDone called with cb == None")
        chain_deferred = BurstDeferred(data = None, parent=self)
        self._ondone = (cb, chain_deferred)     # No chained callbacks like Deferred
        if self._completed:
            chain_deferred._completed = True # propogate the shortcut. TESTING REQUIRED 
            self.callOnDone()
        return chain_deferred

    def callOnDone(self):
        self._completed = True
        if self._ondone:
            cb, chain_deferred = self._ondone
            if expected_argument_count(cb) == 0:
                ret = cb()
            else:
                ret = cb(self._data)
            # is it a deferred? if so tell it to execute the deferred
            # we handed out once it is done.
            if isinstance(ret, BurstDeferred):
                ret.onDone(chain_deferred.callOnDone)

    def onDoneCallDeferred(self, d):
        """ Helper for t.i.d.Deferred mingling - will call this deferred when
        we are done """
        self.onDone(lambda: d.callback(None))

    def getDeferred(self):
        """ Helper for chaining usine DeferredList of chainDeferreds, to avoid
        writing another BurstDeferred version. Returns a Deferred that is called
        when callOnDone is called.
        """
        self._d = Deferred()
        self.onDone(lambda: self._d.callback(None))
        return self._d

# D* - Cacheing

def cached_deferred(filename):
    import os, cPickle
    def wrap(func):
        def cacheit(result):
            failed, fd = False, None
            try:
                fd = open(filename, 'w+')
                cPickle.dump(result, fd)
            except Exception, e:
                failed = True
            finally:
                if fd:
                    fd.close()
            if failed:
                os.unlink(filename)
                print "warning: cache failed, returning uncached results"
                return succeed(result)
            return result # must return for chained callback
        
        def wrapper(*args):
            if not os.path.exists(filename):
                # call function - don't protect this
                deferred = func(*args)
                deferred.addCallback(cacheit)
                return deferred
            # read pickle
            fd = open(filename)
            data = cPickle.load(fd)
            fd.close()
            return succeed(data)
        return wrapper
    return wrap

def cached(filename):
    import os, cPickle
    def wrap(func):
        def wrapper(*args):
            if not os.path.exists(filename):
                # call function - don't protect this
                result = func(*args)
                # write pickle
                failed, fd = False, None
                try:
                    fd = open(filename, 'w+')
                    cPickle.dump(result, fd)
                except Exception, e:
                    failed = True
                finally:
                    if fd:
                        fd.close()
                if failed:
                    os.unlink(filename)
                    print "warning: cache failed, returning uncached results"
                    return result
            # read pickle
            fd = open(filename)
            data = cPickle.load(fd)
            fd.close()
            return data
        return wrapper
    return wrap

# Some Math

def clip(minim, maxim, val):
    return min(maxim, max(minim, val))

def dh_matrix(a, alpha, d, theta):
    """ Denavit Hartenberg Parameters
    a - link length
    alpha - twist
    d - offset
    theta - angle
    """
    ct, st = cos(theta), sin(theta)
    ca, sa = cos(alpha), sin(alpha)
    return [
        [ct, -st*ca, st*sa, a*ct],
        [st, ct*ca, -ct*sa, a*st],
        [0., sa, ca, d],
        [0., 0., 0., 1.]
    ]

def isnumeric(x):
    try:
        i = float(x)
    except:
        return False
    return True

def running_average(window_width):
    samples = [0.0]*window_width
    i = 0
    while 1:
        samples[i] = (yield float(sum(samples))/window_width)
        i = (i + 1) % len(samples)
        #print samples

def running_median(window_width):
    samples = [0.0]*window_width
    i = 0
    while 1:
        samples[i] = (yield sorted(samples)[len(samples)/2])
        i = (i + 1) % len(samples)
        #print sorted(samples)
        #print samples


def transpose(m):
    n_inner = len(m[0])
    return [[inner[i] for inner in m] for i in xrange(n_inner)]

def cumsum(iter):
    """ cumulative summation over an iterator """
    s = 0.0
    for t in iter:
        s += t
        yield s

def grid_points(x_range, y_range):
    from pylab import meshgrid, resize
    n = len(x_range) * len(y_range)
    x, y = meshgrid(x_range, y_range)
    return zip(resize(x,n).tolist(), resize(y,n).tolist())

# Some Trigo
def polar2cart(dist, bearing):
    return cos(bearing)*dist, sin(bearing)*dist

def cart2polar(x, y):
    return sqrt(x**2 + y**2), atan2(y, x)

def calculate_middle((left_dist, left_bearing), (right_dist, right_bearing)):
    target_x = (right_dist * cos(right_bearing) + left_dist * cos(left_bearing)) / 2.0
    target_y = (right_dist * sin(right_bearing) + left_dist * sin(left_bearing)) / 2.0
    return (target_x, target_y)

def calculate_relative_pos((waypoint_x, waypoint_y), (target_x, target_y), offset):
    """ A point k distant (offset) from the waypoint (e.g., ball) along the line connecting the point 
    in the middle of the target (e.g., goal) and the waypoint in the outward direction.

    The coordinate system is the standard: the x axis is to the front,
    the y axis is to the left of the robot. The bearing is measured from the x axis ccw.
    
    computation:
     target - target center (e.g., middle of goal)
     waypoint - waypoint (e.g., ball) - should be of type Locatable (support dist/bearing
     normal - normal pointing from target (goal center) to waypoint (ball)
     result - return result (x, y, bearing)
    """
    
    normal_x, normal_y = waypoint_x - target_x, waypoint_y - target_y # normal is a vector pointing from center to ball
    normal_norm = sqrt(normal_x**2 + normal_y**2)
    normal_x, normal_y = normal_x / normal_norm, normal_y / normal_norm
    result_x, result_y = waypoint_x + offset * normal_x, waypoint_y + offset * normal_y
    #result_norm = (result_x**2 + result_y**2)**0.5
    result_bearing = atan2(-normal_y, -normal_x)
    #print "rel_pos: waypoint(%3.3f, %3.3f), target(%3.3f, %3.3f), n(%3.3f, %3.3f), result(%3.3f, %3.3f, %3.3f)" % (
    #    waypoint_x, waypoint_y, target_x, target_y, normal_x, normal_y, result_x, result_y, result_bearing)
    return result_x, result_y, result_bearing

def normalize2(value, range):
    """ Transform our value into the range of -1..1
    value is assumed within [0,2*range]
    """
    return (value - range) / range

# Text/String/Printing utils

def nicefloat(x):
    try:
        return '%3.3f' % x
    except:
        return str(x)

def nicefloats(l):
    return (' '.join(map(nicefloat, l)))

def trim(s, l):
    """ trims at 3 bytes larger then the supplied value,
    to account for ... added if trimmed
    """
    if len(s) < l + 3:
        return s
    else:
        return s[:l] + '...'

def refilter(exp, it):
    rec = re.compile(exp)
    return [x for x in it if rec.search(x)]

def redir(exp, obj):
    return refilter(exp, dir(obj))

def minimal_title(names):
    """
    compress many similar strings:
    ['/BURST/Loc/Ball/XEst', '/BURST/Loc/Ball/YEst']
     -> '/BURST/Loc/Ball/{XEst, YEst}'
    """
    if len(names) == 0:
        return ''
    if len(names) == 1:
        return names[0]
    n = len(names)
    last = -1
    for i in xrange(min(map(len, names))):
        for j in xrange(n-1):
            if names[j][i] != names[j+1][i]:
                last = i
                break
            if last != -1:
                break
    return '%s{%s}' % (names[0][:last], ', '.join([n[last:] for n in names]))

def compresstoprint(s, first, last):
    if len(s) < first + last + 3:
        return s
    return s[:first] + '\n...\n' + s[-last:]

# Operating System utilities

def get_hostname():
    return os.popen('hostname').read().strip()

def getip():
    return [x for x in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', os.popen('ip addr').read()) if x[:3] != '255' and x != '127.0.0.1' and x[-3:] != '255'][0]

#def not_on_nao():
#    #is_nao = os.popen("uname -m").read().strip() == 'i586'
#    return os.path.exists('/opt/naoqi/bin/naoqi')

# ELF util

ELFCLASS32, ELFCLASS64 = chr(1), chr(2) # taken from the ELF spec
def is_64bit_elf(filename):
    fd = open(filename)
    header = fd.read(16) # size of ELF header
    fd.close()
    ei_class = header[4]
    return ei_class == ELFCLASS64

def is64():
    return sys.maxint != 2**31-1 # actually it's "not is32()" but it is the same

# Python language util

def pairit(n):
    return [n[i:i+2] for i in xrange(0,len(n),2)]

def expected_argument_count(f):
    if hasattr(f, 'im_func'):
        return f.im_func.func_code.co_argcount - 1 # to account for self
    return f.func_code.co_argcount

class CallLogger(object):

    def __init__(self, name, f):
        self._name = name
        self._f = f

    def __call__(self, *args, **kw):
        start = time()
        ret = self._f(*args, **kw)
        end = time()
        print "%s,%3d ms,(%s)" % (self._name, (end - start) * 1000, trim(str(args) + str(kw), 40))
        return ret

class LogCalls(object):

    def __init__(self, name, obj):
        self._obj = obj
        self._name = name

    def __getattr__(self, k):
        f = getattr(self._obj, k) # can throw, which is ok.
        # TODO: use callbacks for motion (isRunning) 
        if k in ('getListData', 'isRunning'):
            return f
        if callable(f):
            return CallLogger('%s.%s' % (self._name, k), f)
        else:
            # hack - just catch the post option of proxies
            if k == 'post':
                return LogCalls('%s.%s' % (self._name, k), f)
        return f

# File utils
def read_ld_so_conf():
    def clean(ls):
        return [x for x in [x.strip() for x in ls] if x!='' and x[:1] != '#']
    conf = clean(linecache.getlines('/etc/ld.so.conf'))
    dirs = [x for x in conf if x != '' and not x.startswith('include')]
    for x in conf:
        if x.startswith('include'):
            for f in glob.glob(x.split()[1]):
                dirs.extend(clean(linecache.getlines(f)))
    return dirs
LD_DEFAULT_PATHS = list(set(['/lib', '/usr/lib'] + read_ld_so_conf()))

def find_in_paths(paths, fname, realpath=True):
    for p in paths:
        p = os.path.join(p, fname)
        if realpath:
            p = os.path.realpath(p)
        if os.path.exists(p):
            return p
    return None

def which(fname, realpath=True):
    return find_in_paths(os.environ['PATH'].split(':'), fname, realpath=realpath)

def whichlib(fname, realpath=True):
    default_dirs = LD_DEFAULT_PATHS
    all_dirs = default_dirs + os.environ['LD_LIBRARY_PATH'].split(':')
    return find_in_paths(all_dirs, fname, realpath=realpath)

# Northern Bites specific, but still standalone

def read_nbfrm(filename, width=320, height=240):
    # doesn't check the version
    # format from Sun May 31 22:34:05 IDT 2009
    # yuv422 image dump (width*height*2 pixels)
    # followed *immediately* by version number as ascii integer,
    # then joints as floats in ascii with one space apart,
    # then all sensors with one space apart
    # currently that's 49 = 1 (version) + 26 + 22
    # sensors:
    #  fsr's: left  foot (front_left, front_right, rear_left, rear_right)   4
    #       : right foot (front_left, front_right, rear_left, rear_right)   4
    #  left foot bumpers (left, right), right foot bumpers (left, right)    4
    #  inertial: accel x, y, z , gyro x, y, angles (computed by naoqi) x, y 7
    #  ultrasound distance, ultrasound sound mode, supportfoot              3
    #                                                                total 22
    sensor_num = 22
    with open(filename) as fd:
        txt = fd.read()
        img_end = width*height*2
        yuv = txt[:img_end]
        variables = txt[img_end:].split()
        version   = int(variables[0])
        variables = map(float, variables[1:])
        joints, sensors = variables[:-sensor_num], variables[-sensor_num:]
    return yuv, version, joints, sensors

def write_nbfrm(filename, yuv, version, joints, sensors):
    with open(filename, 'w+') as fd:
        fd.write(yuv)
        fd.write(str(version) + ' ')
        fd.write(' '.join('%f' % f for f in list(joints) + list(sensors)))

