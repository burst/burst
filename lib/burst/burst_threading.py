from Queue import Queue
from threading import Thread

import burst_target
import burst_util
import burst

if burst_util.is64():
    print "ERROR: ALProxyThread not implemented for pynaoqi yet. can't use --newmove in 64 bits."
    import sys
    sys.exit(-1)

class ALProxyThread(Thread):
    """ New input from aldebaran suggests that ALProxy is blocking,
    but using multiple ALProxys, one per thread, should work. So
    the former ActionThread becomes ALProxyThread, and it won't be
    joined until the very end of the program (which is better anyhow),
    and it will now have an incoming queue to be fed new moves.
    """

    QUIT = False

    def __init__(self, *args, **kw):
        super(ALProxyThread, self).__init__(*args, **kw)
        # XXX First place where Deferred code isn't used - this will blocks..
        self._motion = burst.ALProxy('ALMotion', burst_target.ip, burst_target.port)
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.verbose = burst.options.verbose_movecoordinator

    def start(self, _=None):
        """ convenience for using with Deferred.addCallback """
        return super(ALProxyThread, self).start()

    def run(self):
        while True:
            method_getter, args, bd, description = self.in_queue.get()
            if method_getter == self.QUIT:
                # TODO: need to close the ALProxy somehow
                return
            meth = method_getter(self._motion)
            if self.verbose:
                print "%s: starting  %s" % (self.getName(), description)
            try:
                apply(meth, args)
            except Exception, e:
                print "ActionThread: EXCEPTION: %s" % e
                self.out_queue.put((False, bd, e))
            if self.verbose:
                print "%s: done      %s" % (self.getName(), description)
            self.out_queue.put((True, bd, None))

    def empty(self):
        return self.out_queue.empty()

    def get_if_not_empty(self):
        if self.out_queue.empty():
            return None
        return self.out_queue.get()

    def __iter__(self):
        while not self.out_queue.empty():
            yield self.out_queue.get()

    def put(self, method_getter, args, bd, description):
        self.in_queue.put((method_getter, args, bd, description))

    def quit(self):
        self.in_queue.put((self.QUIT, None, None, None))


