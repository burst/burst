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
brain.player.executeMove(SweetMoves.KICK_A)
"""

half_kick="""
import man.motion.SweeterMoves as SweeterMoves
brain.player.executeMove(SweeterMoves.HALF_KICK)
"""

kick_right="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.KICK_STRAIGHT_RIGHT)
"""

kick_left="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.KICK_STRAIGHT)
"""


sit="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.SIT_A)
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

init="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.INITIAL_POS)
"""

stand="""
import man.motion.SweetMoves as SweetMoves
brain.player.executeMove(SweetMoves.STAND)
"""

command_pairs = [
    ('trace', install_tracer),
    ('traceoff', uninstall_tracer),
    ('walk', walk),
    ('kick', kick),
    ('half_kick', half_kick),
    ('kick_right', kick_right),
    ('kick_left', kick_left),
    ('stand_up_front', stand_up_front),
    ('stand_up_back', stand_up_back),
    ('sit', sit),
    ('look_down', look_down),
    ('stop_walk', stop_walk),
    ('stand', stand),            
    ('init', init),            
    ('stiffness_on', stiffness_on),
    ('stiffness_off', stiffness_off)
]

