# D* - Cacheing

def cached(filename):
    import os, cPickle
    def wrap(func):
        def wrapper(*args):
            if not os.path.exists(filename):
                # write pickle
                failed, fd = False, None
                try:
                    fd = open(filename, 'w+')
                    cPickle.dump(func(*args), fd)
                except Exception, e:
                    failed = True
                finally:
                    if fd:
                        fd.close()
                if failed:
                    os.unlink(filename)
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

def transpose(m):
    n_inner = len(m[0])
    return [[inner[i] for inner in m] for i in xrange(n_inner)]
 
