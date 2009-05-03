# really simple debug loop

import socket
def getline(s):
    a = []
    c = s.recv(1)
    a.append(c)
    while c!='\n':
        c = s.recv(1)
        a.append(c)
    return ''.join(a[:-1])

class Environment(object):
    def doeval(self, l):
        return eval(l)
    def doexec(self, l):
        exec(l)

PORT=9909
def opendebugsocket():
    print "debug socket: listening to %s" % PORT
    sa = socket.socket()
    sa.bind(('localhost', PORT))
    sa.listen(1)
    s, origin = sa.accept()
    env = Environment() # to avoid hitting these variables when exec-ing, like
                        # overwrite s
    while True:
        l = getline(s)
        if not l:
            print "done"
            break
        try:
            s.send(repr(env.doeval(l))+'\n')
        except:
            try:
                env.doexec(l)
            except:
                s.send('error\n')
            else:
                s.send('ok\n')


