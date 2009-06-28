"""
Implements a read eval loop over a socket which doesn't block at any stage (not
in bind, in accept, or in reading the socket), and which uses either eval
or code.InteractiveConsole.do_interactive to interact with the interpreter.

It relies on the following modules which are standard but not by default in
openembedded (and opennao) distributions:

socket
code

Usage:
debug_socket = DebugSocket(port=20000)
debug_socket.setvar('brain', brain_instance)
# ... sometime later
debug_socket.tryReadEval()
"""

import socket
import code

def getline(s, c):
    print "getting line"
    a = []
    a.append(c)
    while c!='\n':
        c = s.recv(1)
        a.append(c)
    return ''.join(a[:-1])

class Environment(object):

    def __init__(self):
        self.ic = code.InteractiveConsole()

    def do_eval_or_interactive(self, l):
        """ returns the evaluated expression or none. In case
        of syntax error, still returns none, but prints to stdout
        'syntax error'
        """
        print "do_eval_or_interactive", l
        try:
            c = compile(l, 'mansh_debugsocket_eval', 'eval')
        except:
            pass
        else:
            print "compile as eval worked, returning"
            return eval(l)
        self.do_interactive(l)
        return None

    def do_interactive(self, l):
        try:
            print "pushing to interactive console"
            self.ic.push(l)
        except:
            print "syntax error"
        return None

    def setvar(self, k, v):
        setattr(self, k, v)
        self.ic.locals[k] = v

class DebugSocket(object):

    def __init__(self, port):
        self.port = port
        self.host = '0.0.0.0' # you may want 'localhost' for more privateness..
        self.has_connection = False
        self.sa = None
        self.s = []
        self.open()

    def runLoop(self):
        while True:
            self.tryReadEval();

    def open(self):
        print "debug socket: listening to %s" % self.port
        self.sa = sa = socket.socket()
        self.tryBind()
        # to avoid hitting these variables when exec-ing, like
        # overwrite s
        self.env = Environment()

    def tryBind(self):
        if self.sa.getsockname() == (self.host, self.port):
            return True
        try:
            print "BIND: trying to bind"
            self.sa.bind((self.host, self.port))
        except Exception, e:
            self.port += 1
            print "BIND:", e
            print "next time try to bind to %s" % self.port
            return False
        else:
            print "bound to (%s, %s)" % (self.host, self.port)
        self.sa.listen(20)
        self.sa.setblocking(False)
        return True

    def setvar(self, k, v):
        self.env.setvar(k, v)

    def tryAccept(self):
        if not self.tryBind():
            self.has_connection = False
            return self.has_connection
        try:
            s, origin = self.sa.accept()
        except:
            pass
        else:
            print "accepted connection"
            self.s.append(s)
            s.setblocking(False)
            self.has_connection = True
        return self.has_connection

    def readLines(self):
        self.tryAccept()
        deleted_socks = []
        msgs = []
        for i, s in enumerate(self.s):
            try:
                c = s.recv(1)
            except:
                continue
            if c == '': # closed socket
                deleted_socks.append(i) # just cleanup
                continue
            s.setblocking(True)
            l = getline(s, c)
            s.setblocking(False)
            msgs.append((s, l))
        for i in reversed(deleted_socks):
            del self.s[i]
        self.has_connection = (len(self.s) == 0)
        return msgs

    def tryReadEval(self):
        msgs = self.readLines()
        if len(msgs) == 0:
            return
        for s, l in msgs:
            if len(l) == 0: continue
            if l[0] == '#':
                # TODO: no care is taken to not intermingle lines from different
                # sockets - deemed overkill (even multiple sockets are just nice to have)
                print "starts with hash (#), execing"
                self.env.do_interactive(l[1:])
                s.send('ok\n')
                return
            if not l:
                return
            try:
                print "got", repr(l)
                s.send(repr(self.env.do_eval_or_interactive(l))+'\n')
                return
            except Exception, e:
                print "exception in do_eval_or_interactive:"
                print e
                s.send('error\n')

    def set_module_global(self, k, v):
        self.env.setvar(k, v)
        globals()[k] = v

