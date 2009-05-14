#!/usr/bin/env python

"""
shell to test Man module. Connects to the debugsocket.DebugSocket instance
in Brain on port 20000 (set in noggin/Brain.py, Brain.__init__)

Provides command completion (via tab) and history (saved in ~/.mansh_history)
also provides "macros" via the nogging/util/mansh_commands.py file, used
for testing/developing kicks/motions.

Seems to be safe for usage since it is run when the other python code is
to be run, and from within the python interpreter (as opposed to previous
approaches of sending code via the soap interface to run PySimpleEval)

Usage:
to connect to localhost, no parameters are required
to connect to a robot, use --ip <hostname/ip> (despite the argument name
you don't have to supply an ip address)

Example usage - get ball dist via localization dist:

$ mansh.py
['trace', 'traceoff', 'walk', 'kick', 'half_kick', 'almost_kick', 'kick_right', 'kick_left', 'stand_up_front', 'stand_up_back', 'sit', 'look_down', 'stop_walk', 'stand', 'init', 'stiffness_on', 'stiffness_off']
connecting to debug shell on localhost:20000
eval>> # (pressed Tab Tab to get the default commands)
almost_kick     kick            look_down       stand_up_back   stop_walk
c               kick_left       self            stand_up_front  trace
half_kick       kick_right      sit             stiffness_off   traceoff
init            l               stand           stiffness_on    walk
eval>>brain.ball.locDist, brain.ball.dist
(103.01202391345397, 103.25756072998047)
"""

import readline
import cPickle
import os
import code

from socket import socket

from mansh_commands import command_pairs

HISTORY_FILE=os.path.join(os.getenv('HOME'), '.mansh_history')

def execer(txt):
    exec(txt)

class Main:
    def __init__(self):
        if os.path.exists(HISTORY_FILE):
            readline.read_history_file(HISTORY_FILE)
        self.remote_dir_cache = {}
        self.completer_cache = {}
        self.command_so_far = ''
        self.command_names = [x[0] for x in command_pairs]
        self.first_char = ''
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)
        self.man_func = self.evalOrExec
        self.state = 'eval'
        self.state_func = {'eval': self.switchToEval,
            'exec': self.switchToExec,
            'local': execer
            }
        print 'available macro commands:'
        print ', '.join(self.command_names)
        self.cmds = dict([(k, lambda txt=txt, self=self: self.execIt(txt)) for k, txt in command_pairs])
        self.states = self.state_func.keys()

    def completer(self, text, state):
        possibilities = self.get_completion_possibilities(text)
        if len(possibilities) == 0 or state > len(possibilities):
            return None # only if there was an error completing this
        return possibilities[state]

    def get_completion_possibilities(self, text):
        """ find all completions for text. We currently look at two places:
        commands - the macros defined in mansh_commands
        dir() for the part before the rightmost dot remotely (cached)

        The whole list itself is also cached (but the dir is cached seperately)
        """
        if text in self.completer_cache:
            return self.completer_cache[text]
        parts = text.rsplit('.', 1)
        if len(parts) == 1:
            base, rest = '', text
        else:
            assert(len(parts) == 2)
            base, rest = parts[0], parts[1]
        if base not in self.remote_dir_cache:
            # expensive path - roundtrip'ing
            dir_result = self.evalOrExec('dir(%s)' % base)
            try:
                # Note: evaling random strings..
                l = eval(dir_result)
            except:
                # no completions
                l = []
            self.remote_dir_cache[base] = l
        possibilities = [x for x in self.remote_dir_cache[base] if x.startswith(rest)]
        if base == '':
            possibilities += [x for x in self.command_names if x.startswith(rest)]
        else:
            # we have some x.y.z.rest to complete (rest can be nothing)
            possibilities = ['%s.%s' % (base, p) for p in possibilities]
        self.completer_cache[text] = possibilities
        return possibilities

    def switchToExec(self):
        return self.execIt

    def switchToEval(self):
        return self.evalOrExec

    def parse_cl_args(self):
        """ Parse Command line Arguments """
        import optparse
        parser = optparse.OptionParser()
        parser.add_option('','--ip', dest='ip', default='localhost', help='ip to connect to (ok, host too, misnamed)')
        parser.add_option('','--port',type=int, dest='port', default=20000, help='port to connect to')
        options, rest = parser.parse_args()
        self.options = options

    def main(self):
        self.parse_cl_args()
        host, port = self.options.ip, self.options.port
        print "connecting to %s:%s" % (host, port)
        self.s = socket()
        try:
            self.s.connect((host, port))
        except Exception, e:
            print "connection failed, quitting"
            raise SystemExit

        try:
            self.mainloop()
        except RuntimeError, e:
            print e
            print "You probably killed the naoqi at the other end of the rainbow. You should restart it"
        except (KeyboardInterrupt, EOFError):
            pass
        print "writing readline history file to %s" % HISTORY_FILE
        readline.write_history_file(HISTORY_FILE)

    def mainloop(self):
        last = None
        while True:
            prompt = "%s>>" % self.state
            cmd = raw_input(prompt).strip()
            if len(cmd) == 0:
                continue
            if cmd in self.states:
                self.man_func = self.state_func[cmd]()
                self.state = cmd
                continue
            elif cmd in self.cmds.keys():
                self.cmds[cmd]()
                continue
            res = self.man_func(cmd)
            if self.state != 'eval':
                continue
            if res == 'error':
                print "ERROR"
            else:
                last = res
                print res

    def evalOrExec(self, s):
        """ Implements an interpretation loop, but without execution, for
        testing of the expression before sending it to the debugserver on
        Brain.
        """
        if len(s) == 0: return
        first_char = '#'
        try:
            compile(s, 's', 'eval')
            first_char = ''
        except:
            if len(self.command_so_far) != 0 and self.command_so_far[-1] != '\n':
                self.command_so_far = self.command_so_far + '\n'
            self.command_so_far = self.command_so_far + s
            try:
                result = code.compile_command(self.command_so_far)
            except Exception, e:
                print "compilation error as : %s" % e
                self.command_so_far = ''
                return
            if result is not None:
                self.command_so_far = ''
        if s[-1] != '\n': s = s + '\n'
        s = first_char + s
        self.s.send(s)
        return self.getLine()

    def execIt(self, s):
        lines = [l for l in s.split('\n') if len(l.strip()) > 0 and l.strip()[0] != '#']
        to_send = '\n'.join('#%s' % l for l in lines) + '\n'
        print "sending", repr(to_send)
        self.s.send(to_send)
        returned_lines = [self.getLine() for i in xrange(len(lines))]
        return '%s - %s' % (len(returned_lines), ','.join(returned_lines))

    def getLine(self):
        c = self.s.recv(1)
        bytes = [c]
        while bytes[-1] != '\n':
            bytes.append(self.s.recv(1))
        return ''.join(bytes[:-1])

if __name__ == '__main__':
    Main().main()

