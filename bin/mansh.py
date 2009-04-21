#!/usr/bin/env python

"""
shell to test Man module, i.e. nao-man.
uses burst, so all the regular command line arguments apply,
including --ip and --port.
"""

import readline
import cPickle
import os

import burst

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

def execer(txt):
    exec(txt)

class Main:
    def __init__(self):
        if os.path.exists(HISTORY_FILE):
            readline.read_history_file(HISTORY_FILE)
        burst.init()

    def main(self):
        self.man = burst.ALProxy('Man')

        print self.man.getMethodList()

        self.man_func = self.man.pyEval
        self.state = 'eval'
        self.state_func = {'eval': self.man.pyEval,
            'exec': self.man.pyExec, 'local': execer
            }
        self.cmds = {'trace': lambda: self.man.pyExec(install_tracer),
            'traceoff': lambda: self.man.pyExec(uninstall_tracer)}
        self.states = self.state_func.keys()
        try:
            self.mainloop()
        except (KeyboardInterrupt, EOFError):
            print "writing readline history file to %s" % HISTORY_FILE
            readline.write_history_file(HISTORY_FILE)

    def mainloop(self):
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
                try:
                    last = cPickle.loads(res)
                except:
                    print "Error unpickling, returning raw result"
                    last = res
                print last


if __name__ == '__main__':
    Main().main()

