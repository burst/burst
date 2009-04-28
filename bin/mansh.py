#!/usr/bin/env python

"""
shell to test Man module, i.e. nao-man.
uses burst, so all the regular command line arguments apply,
including --ip and --port.
"""

import readline
import cPickle
import os

from socket import socket

HISTORY_FILE=os.path.join(os.getenv('HOME'), '.mansh_history')

uninstall_tracer="""
import sys
sys.settrace(None)
"""

install_tracer="""
def one(frame, what, gad):
    code=frame.f_code
    filename=code.co_filename
    line=code.co_firstlineno
    try:
        fd=open(filename)
        theline=fd.readlines()[line-1]
        fd.close()
    except:
        theline=('%s: %s' % (filename, line))[:80]
    print theline

import sys
sys.settrace(one)
"""

stiffness_on="""
import man.motion as motion
motion.MotionInterface().sendStiffness(motion.StiffnessCommand(0.8))
"""

stiffness_off="""
import man.motion as motion
motion.MotionInterface().sendStiffness(motion.StiffnessCommand(0.0))
"""

walk="""
import man.motion as motion
motion.MotionInterface().setNextWalkCommand(motion.WalkCommand(1.5,0.0,0.0))
"""

stop_walk="""
import man.motion as motion
motion.MotionInterface().resetWalk()
"""

kick="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.KICK_STRAIGHT)
"""

sit="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.SIT_POS)
"""

look_down="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.NEUT_HEADS)
"""

stand_up_front="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.STAND_UP_FRONT)
"""

stand_up_back="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.STAND_UP_BACK)
"""


def execer(txt):
    exec(txt)

class Main:
    def __init__(self):
        if os.path.exists(HISTORY_FILE):
            readline.read_history_file(HISTORY_FILE)
        self.completer_cache = {}
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
        self.state_func = {'eval': self.evalOrExec,
            'local': execer
            }
        self.cmds = dict([(k, lambda txt=txt, self=self: self.execIt(txt)) for k, txt in [
            ('trace', install_tracer),
            ('traceoff', uninstall_tracer),
            ('walk', walk),
            ('kick', kick),
            ('stand_up_front', stand_up_front),
            ('stand_up_back', stand_up_back),
            ('sit', sit),
            ('look_down', look_down),
            ('stop_walk', stop_walk),
            ('stiffness_on', stiffness_on),
            ('stiffness_off', stiffness_off)]])
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
                self.man_func = self.state_func[cmd]
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
        if len(s) == 0: return
        try:
            compile(s, 's', 'eval')
        except:
            try:
                compile(s, 's', 'exec')
            except Exception, e:
                print "compilation error as exec: %s" % e
                return
        if s[-1] != '\n': s = s + '\n'
        self.s.send(s)
        return self.getLine()

    def execIt(self, s):
        self.s.send(s)
        return self.getLine()

    def getLine(self):
        c = self.s.recv(1)
        bytes = [c]
        while bytes[-1] != '\n':
            bytes.append(self.s.recv(1))
        return ''.join(bytes[:-1])

if __name__ == '__main__':
    Main().main()

