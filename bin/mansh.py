#!/usr/bin/env python

import burst
import cPickle

# use --ip, --port to this shell

def execer(txt):
    exec(txt)

def main():
    burst.init()
    man=burst.ALProxy('Man')

    print man.getMethodList()

    man_func = man.pyEval
    state = 'eval'
    state_func = {'eval': man.pyEval, 'exec': man.pyExec, 'local': execer}
    states = state_func.keys()
    while True:
        print "%s>>" % state,
        cmd = raw_input()
        if cmd in states:
            man_func = state_func[cmd]
            state = cmd
            continue
        res = man_func(cmd)
        if state != 'eval':
            continue
        if res == 'error':
            print "ERROR"
        else:
            last = cPickle.loads(res)
            print last

if __name__ == '__main__':
    main()

