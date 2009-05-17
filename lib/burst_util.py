# ELF util

# are we on 64 bit or 32 bit? if on 64, use pynaoqi (and tell user)
ELFCLASS32, ELFCLASS64 = 1, 2 # taken from
def is64():
    fd = open('/bin/sh') # some executable that should be on all systems
    header = fd.read(16) # size of ELF header
    fd.close()
    ei_class = header[4]
    return ei_class == ELFCLASS64

# Twisted-like Deferred and succeed

class MyDeferred(object):
    """ mimic in the most minimal way twisted.internet.defer.Deferred """
    def __init__(self):
        self._cb = None
        self.called = 0
        # not setting self.result to mimic bug/feature in original

    def addCallback(self, f):
        """ not implementing chained callbacks for now """
        self._cb = f
        if self.called: # call immediately
            self.result = f(self.result) # saved for filter effect

    def callback(self, result):
        self.called = True
        self.result = result
        if self._cb:
            self._cb(result)

def succeed(result):
    d = Deferred()
    d.callback(result)
    return d

try:
    # use the real thing if it is there
    from twisted.internet.defer import Deferred
except:
    Deferred = MyDeferred

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

# Stuff

def getip():
    return [x for x in re.findall('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', os.popen('ifconfig').read()) if x[:3] != '255' and x != '127.0.0.1' and x[-3:] != '255'][0]

def not_on_nao():
    #is_nao = os.popen("uname -m").read().strip() == 'i586'
    return os.path.exists('/opt/naoqi/bin/naoqi')

def compresstoprint(s, first, last):
    if len(s) < first + last + 3:
        return s
    return s[:first] + '\n...\n' + s[-last:]

def cumsum(iter):
    """ cumulative summation over an iterator """
    s = 0.0
    for t in iter:
        s += t
        yield s

def running_average(window_width):
    samples = [0.0]*window_width
    i = 0
    while 1:
        samples[i] = (yield float(sum(samples))/window_width)
        i = (i + 1) % len(samples)
        #print samples

def transpose(m):
    n_inner = len(m[0])
    return [[inner[i] for inner in m] for i in xrange(n_inner)]
 
