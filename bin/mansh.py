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
        burst.init()

    def main(self):
        self.man = burst.ALProxy('Man')

        print self.man.getMethodList()

        self.man_func = self.man.pyEval
        self.state = 'eval'
        self.state_func = {'eval': self.man.pyEval,
            'exec': self.man.pyExec, 'local': execer
            }
        self.cmds = dict([(k, lambda txt=txt, self=self: self.man.pyExec(txt)) for k, txt in [
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

