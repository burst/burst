#!/usr/bin/env python

"""
shell to test Man module, i.e. nao-man.
uses burst, so all the regular command line arguments apply,
including --ip and --port.
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
        self.completer_cache = {}
        self.command_so_far = ''
        self.first_char = ''
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)

    def completer(self, text, state):
        # look for the last part before a '.', including everything, in the globals
        # locally first (cache), then across the socket.
        parts = text.rsplit('.', 1)
        if len(parts) == 1: # we can't complete without a comma to guide us (not right now)
            base, rest = '', text
        else:
            assert(len(parts) == 2)
            base, rest = parts[0], parts[1]
        if base not in self.completer_cache:
            # expensive path - roundtrip'ing
            dir_result = self.evalOrExec('dir(%s)' % base)
            try:
                # Note: evaling random strings..
                l = eval(dir_result)
            except:
                # no completions
                l = []
            self.completer_cache[base] = l
        possibilities = [x for x in self.completer_cache[base] if x.startswith(rest)]
        if len(possibilities) == 0 or state > len(possibilities):
            return None # only if there was an error completing this
        if len(parts) == 1: # simple case - just a word to complete
            return possibilities[state]
        # default case - we have some x.y.z.rest to complete (rest can be nothing)
        return '%s.%s' % (base, possibilities[state])

    def switchToExec(self):
        return self.execIt

    def switchToEval(self):
        return self.evalOrExec

    def main(self):
        host, port = 'localhost', 20000
        print "connecting to debug shell on %s:%s" % (host, port)
        self.s = socket()
        try:
            self.s.connect((host, port))
        except Exception, e:
            print "connection failed, quitting"
            raise SystemExit

        self.man_func = self.evalOrExec
        self.state = 'eval'
        self.state_func = {'eval': self.switchToEval,
            'exec': self.switchToExec,
            'local': execer
            }
        print [x[0] for x in command_pairs]
        self.cmds = dict([(k, lambda txt=txt, self=self: self.execIt(txt)) for k, txt in command_pairs])
        self.states = self.state_func.keys()
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
            cmd = raw_input(prompt)
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
        print "sending %r" % s
        self.s.send(s)
        return self.getLine()

    def execIt(self, s):
        lines = [l for l in s.split('\n') if len(l.strip()) > 0 and l.strip()[0] != '#']
        to_send = '\n'.join('#%s' % l for l in lines) + '\n'
        print "sending", repr(to_send)
        self.s.send(to_send)
        return self.getLine()

    def getLine(self):
        c = self.s.recv(1)
        bytes = [c]
        while bytes[-1] != '\n':
            bytes.append(self.s.recv(1))
        return ''.join(bytes[:-1])

if __name__ == '__main__':
    Main().main()

