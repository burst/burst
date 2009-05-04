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

