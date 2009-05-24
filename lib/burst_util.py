import os
import re
from time import time

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
        self._callbacks.append(f)
        if self.called: # call immediately
            self.result = f(self.result) # saved for filter effect
        return self

    def callback(self, result):
        self.called = True
        self.result = result
        for cb in self._callbacks:
            try:
                self.result = cb(self.result)
            except Exception, e:
                # This is where an errback would have been triggered in
                # the real t.i.d.Deferred
                print "Exception on deferred: %s" % str(e)
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
        # TODO: shortcutting. How the fuck do I call the cb immediately without
        # giving a chance to the caller to use the chain_deferred??

        # will be called by cb's return deferred, if any
        if cb is None:
            raise Exception("onDone called with cb == None")
        chain_deferred = BurstDeferred(data = None, parent=self)
        self._ondone = (cb, chain_deferred)
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

# Text/String/Printing utils

def nicefloats(l):
    return (' '.join(['%3.3f']*len(l))) % tuple(l)

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

def not_on_nao():
    #is_nao = os.popen("uname -m").read().strip() == 'i586'
    return os.path.exists('/opt/naoqi/bin/naoqi')

# ELF util

ELFCLASS32, ELFCLASS64 = chr(1), chr(2) # taken from the ELF spec
def is64():
    fd = open('/bin/sh') # some executable that should be on all systems
    header = fd.read(16) # size of ELF header
    fd.close()
    ei_class = header[4]
    return ei_class == ELFCLASS64

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
        if callable(f):
            return CallLogger('%s.%s' % (self._name, k), f)
        else:
            # hack - just catch the post option of proxies
            if k == 'post':
                return LogCalls('%s.%s' % (self._name, k), f)
        return f

