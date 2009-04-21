#!/usr/bin/env python

import readline
import cPickle
import os

import burst

HISTORY_FILE=os.path.join(os.getenv('HOME'), '.mansh_history')

# use --ip, --port to this shell

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
            'exec': self.man.pyExec, 'local': execer}
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
            res = self.man_func(cmd)
            if self.state != 'eval':
                continue
            if res == 'error':
                print "ERROR"
            else:
                last = cPickle.loads(res)
                print last


if __name__ == '__main__':
    Main().main()

