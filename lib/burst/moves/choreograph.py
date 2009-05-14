"""
Moves that were created by choreograph. To add a new move:

HOWTO
=====

To define a new function using the python generated code from choreograph:

@chorwrap
def MY_MOVE():
    <paste code from choreograph>
    return jointCodes, angles, times

To use this:

from burst.moves import MY_MOVE
class Me(Player):
    ...
    def doSomething(self):
        self._actions.executeMoveChoreograph(MY_MOVE)

"""

def chorwrap(f):
    return f()

def mirrorChoreographMove(jointCodes, angles, times):
    """ Usage:
    GET_UP_BACK_MIR = mirrorChoreographMove(GET_UP_BACK)
    """
    newJointCodes = [{'L':'R','R':'L'}.get(jc[0], jc[0]) + jc[1:] for jc in jointCodes]
    return newJointCodes, angles, times

@chorwrap
def GET_UP_BACK():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(0.00000), float(0.00000), float(-0.78540), float(0.00000), float(0.34907), float(0.32823), float(0.33129), float(0.37886), float(0.37886), float   (0.37886), float(0.27925)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("HeadYaw")
    angles.append([float(0.00000), float(-0.00000), float(0.00000), float(0.00000), float(0.00000), float(-0.00744), float(-0.01070), float(-0.00940), float(-0.00940), float(-0.00940)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.24435), float(0.24435), float(0.24435), float(0.78540), float(-0.57065), float(-1.22173), float(-1.22173), float(-1.22173), float(-1.22173), float(-0.17453)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(-0.39573), float(-0.10379), float(0.11810), float(0.08727), float(0.00000), float(0.00000)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(-1.65806), float(-0.69813), float(0.00000), float(-0.48869), float(-0.82372), float(-0.80535), float(-0.80535), float(-1.13446), float(-1.25664)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.15708), float(0.08727), float(0.08727), float(0.08727), float(0.08295), float(0.09445), float(0.08308), float(0.08308), float(-1.25664), float(-1.23918)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.00000), float(-0.17453), float(-0.17453), float(-1.57080), float(-1.57080), float(-0.85706), float(0.38551), float(-0.85521), float(-0.83599), float(-0.87266), float(-0.17453)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.54105), float(0.15498), float(-0.29142), float(0.19199), float(0.36652), float(0.00000), float(-0.01047)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(-0.00000), float(-0.66323), float(-0.49909), float(-0.85897), float(-0.40225), float(-0.40225), float(0.00000), float(0.00000)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(1.67552), float(1.67552), float(1.67552), float(1.67552), float(2.20124), float(1.77479), float(2.20585), float(2.20585), float(2.09440), float(0.34907)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.00000), float(2.09440), float(2.09440), float(2.09440), float(2.09440), float(0.69813), float(0.74074), float(0.73321), float(0.73321), float(1.71042), float(1.83260)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(1.57080), float(0.80285), float(0.47124), float(0.36652), float(0.00000), float(1.04720), float(0.49851), float(0.49851), float(0.49851), float(0.03491), float(0.19199)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.24435), float(0.24435), float(0.24435), float(0.78540), float(0.78540), float(0.69115), float(0.40317), float(-0.57945), float(-1.22173), float(-0.17453)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00929), float(-0.12915), float(0.67960), float(0.27751), float(0.00000), float(0.00000)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(1.65806), float(0.69813), float(0.00000), float(0.07205), float(0.05819), float(0.45379), float(0.55995), float(1.13446), float(1.25664)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(-0.15708), float(-0.08727), float(-0.08727), float(-0.08727), float(-0.08080), float(-0.08241), float(0.00062), float(0.00062), float(1.25664), float(1.23918)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.00000), float(-0.17453), float(-0.17453), float(-1.57080), float(-1.57080), float(-1.52484), float(-1.55965), float(-0.90583), float(-0.90583), float(-0.87266), float(-0.17453)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(-0.54105), float(-0.55842), float(-0.56600), float(-0.29671), float(-0.01745), float(0.00000), float(0.01047)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(-0.00000), float(-0.66323), float(-0.49909), float(-0.85897), float(-0.40225), float(-0.40225), float(0.00000), float(0.00000)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(1.67552), float(1.67552), float(1.67552), float(1.67552), float(1.22173), float(1.08036), float(0.87616), float(1.76278), float(2.09440), float(0.34907)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.00000), float(2.09440), float(2.09440), float(2.09440), float(2.09440), float(2.09440), float(1.77434), float(0.89131), float(0.89131), float(1.71042), float(1.83260)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-1.57080), float(-0.80285), float(-0.47124), float(-0.36652), float(0.00000), float(-0.57596), float(-0.27770), float(-0.87266), float(-0.68068), float(-0.03491), float(-0.19199)])
    times.append([float(0.90000), float(1.90000), float(2.70000), float(3.40000), float(3.90000), float(4.90000), float(5.80000), float(6.80000), float(7.30000), float(8.40000), float(9.40000)])

    return jointCodes, angles, times

@chorwrap
def GET_UP_BELLY():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(-0.57596), float(0.00000), float(-0.34907), float(-0.48869), float(0.00000), float(0.27925)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(5.20000), float(6.20000), float(8.40000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(-1.13446), float(-1.13446), float(-0.78365), float(0.08727), float(-0.31241), float(-0.71558), float(-1.04720), float(-0.17453)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(-0.68068), float(-0.55501), float(-0.29671), float(-0.10472), float(0.00000), float(0.00000)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000), float(-0.61087), float(-1.65806), float(-0.13963), float(-0.71558), float(-1.29154), float(-1.39626), float(-1.25664)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(-1.57080), float(-1.57080), float(-1.57080), float(-1.57080), float(-0.24435), float(-0.92502), float(-1.57080), float(-1.23918)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.00000), float(-1.57080), float(-1.57080), float(-1.57080), float(-1.57080), float(-1.06989), float(-1.04720), float(-0.17453)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.08727), float(0.10472), float(-0.01047), float(-0.01047)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(-0.87266), float(-0.87266), float(-0.96517), float(-0.78540), float(0.00000), float(0.00000)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LKneePitch")
    angles.append([float(2.09440), float(2.09440), float(1.04720), float(1.01229), float(2.15548), float(2.16421), float(2.09440), float(0.34907)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(-1.57080), float(-0.87266), float(-0.17453), float(0.00000), float(0.61087), float(1.11701), float(1.62316), float(1.83260)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.03491), float(0.13090), float(0.17453), float(0.19199)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(-1.13446), float(-1.13446), float(-0.78365), float(0.08727), float(-0.31241), float(-0.71558), float(-1.04720), float(-0.17453)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.68068), float(0.55501), float(0.29671), float(0.10472), float(0.00000), float(0.00000)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.61087), float(1.65806), float(0.13963), float(0.71558), float(1.29154), float(1.39626), float(1.25664)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(1.57080), float(1.57080), float(1.57080), float(1.57080), float(0.24435), float(0.92502), float(1.57080), float(1.23918)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.00000), float(-1.57080), float(-1.57080), float(-1.57080), float(-1.57080), float(-1.06989), float(-1.04720), float(-0.17453)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(-0.08727), float(-0.10472), float(0.01047), float(0.01047)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(-0.87266), float(-0.87266), float(-0.96517), float(-0.78540), float(0.00000), float(0.00000)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RKneePitch")
    angles.append([float(2.09440), float(2.09440), float(1.04720), float(1.01229), float(2.15548), float(2.16421), float(2.09440), float(0.34907)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(-1.57080), float(-0.87266), float(-0.17453), float(0.00000), float(0.61087), float(1.11701), float(1.62316), float(1.83260)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(-0.03491), float(-0.13090), float(-0.17453), float(-0.19199)])
    times.append([float(1.40000), float(2.40000), float(3.70000), float(4.40000), float(5.20000), float(6.20000), float(7.40000), float(8.40000)])

    return jointCodes, angles, times
