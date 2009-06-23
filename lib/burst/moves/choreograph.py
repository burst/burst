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
    GET_UP_BACK_MIRROR = mirrorChoreographMove(GET_UP_BACK)
    """

    # Flip Left/Right
    def flipLR(jointCode):
        if jointCode in ['LHipYawPitch', 'RHipYawPitch']:
            return jointCode
        return {'L':'R','R':'L'}.get(jointCode[0], jointCode[0]) + jointCode[1:]

    newJointCodes = [flipLR(jointCode) for jointCode in jointCodes]

    # Switch sign of Roll/Yaw joints
    newAngles = list(angles)
    for jointIndex, jointcode in enumerate(jointCodes):
        if ('Roll' in jointcode or 'Yaw' in jointcode) and not 'YawPitch' in jointcode:
            newAngles[jointIndex] = [-x for x in newAngles[jointIndex]]
    return newJointCodes, newAngles, times

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

@chorwrap
def GOALIE_LEAP_RIGHT():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(0.00609), float(-0.00004), float(-0.00004)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("HeadYaw")
    angles.append([float(0.00149), float(-0.00004), float(-0.00004)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(-0.67807), float(0.55833), float(0.56907)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(-0.25767), float(-0.12575), float(-0.13342)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(-0.69793), float(-1.25017), float(-1.26532)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(-0.57376), float(-0.55228), float(-0.54624)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHand")
    angles.append([float(-0.99052), float(-0.25001), float(-0.25001)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.38806), float(-1.34067), float(-0.63197)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHipRoll")
    angles.append([float(-0.39420), float(-0.32977), float(-0.26841)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.06899), float(0.00004), float(0.00004)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LKneePitch")
    angles.append([float(1.17193), float(0.00456), float(0.00303)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(1.28392), float(0.73014), float(0.71212)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.10274), float(0.00868), float(0.00868)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LWristYaw")
    angles.append([float(-0.02919), float(-1.25783), float(-1.25840)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(-1.22173), float(-1.22169), float(0.78535)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(-0.10734), float(-0.00609), float(0.07828)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(1.54785), float(1.57086), float(0.20100)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(1.41124), float(1.41431), float(0.63964)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RHand")
    angles.append([float(-0.99234), float(-1.00000), float(-1.00000)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RHipPitch")
    angles.append([float(-1.17969), float(-1.30087), float(0.07973)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RHipRoll")
    angles.append([float(-0.77463), float(-0.12575), float(0.20867)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RKneePitch")
    angles.append([float(2.19060), float(2.18906), float(0.00464)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(1.55398), float(0.47251), float(-1.55390)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-1.36223), float(-1.22417), float(-0.09975)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RWristYaw")
    angles.append([float(2.35771), float(1.25659), float(1.25659)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    return jointCodes, angles, times

#GOALIE_LEAP_LEFT = mirrorChoreographMove(*GOALIE_LEAP_RIGHT)

@chorwrap
def GOALIE_LEAP_LEFT():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(0.00609), float(0.00609), float(0.00609)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("HeadYaw")
    angles.append([float(0.00149), float(0.00149), float(0.00149)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(-1.22173), float(-1.22168), float(0.78537)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.10474), float(0.00608), float(-0.07829)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(-1.54786), float(-1.56214), float(-0.20101)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(-1.41123), float(-1.41429), float(-0.63962)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHand")
    angles.append([float(-0.99991), float(-0.99991), float(-0.99991)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHipPitch")
    angles.append([float(-1.17970), float(-1.30089), float(0.07971)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.77462), float(0.12573), float(-0.20868)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.06899), float(-0.06899), float(-0.06899)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LKneePitch")
    angles.append([float(2.19060), float(2.18908), float(0.00466)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(1.55400), float(0.47253), float(-1.55389)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(1.36225), float(1.22419), float(0.09976)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("LWristYaw")
    angles.append([float(-1.82378), float(-1.82378), float(-1.82378)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(-0.67808), float(0.55832), float(0.56906)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.25766), float(0.12573), float(0.13340)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.69792), float(1.25016), float(1.26530)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.57377), float(0.55229), float(0.54625)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RHand")
    angles.append([float(-0.99991), float(-0.99991), float(-0.99991)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.38805), float(-1.34066), float(-0.63195)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.39418), float(0.32976), float(0.26840)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RKneePitch")
    angles.append([float(1.17192), float(0.00455), float(0.00301)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(1.28390), float(0.73013), float(0.71210)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.10272), float(-0.00867), float(-0.00867)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    jointCodes.append("RWristYaw")
    angles.append([float(1.82378), float(1.82378), float(1.82378)])
    times.append([float(0.40000), float(0.80000), float(1.20000)])

    return jointCodes, angles, times

@chorwrap
def CIRCLE_STRAFE_CLOCKWISE():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.00000), float(-0.09250), float(-0.11868), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipRoll")
    angles.append([float(-0.08727), float(0.00698), float(0.00698), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.01745), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180), float(0.26180), float(0.26180), float(0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHand")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.08727), float(-0.10996), float(-0.10996), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RHipRoll")
    #angles.append([float(-0.00873), float(-0.2), float(-0.13962), float(0.00000), float(0.00000)]) # cech 16cm
    #angles.append([float(-0.00873), float(-0.19), float(-0.13962), float(0.00000), float(0.00000)]) # gerrard
    #angles.append([float(-0.00873), float(-0.185), float(-0.13962), float(0.00000), float(0.00000)]) # messi - 20
    angles.append([float(-0.00873), float(-0.21642), float(-0.13962), float(0.00000), float(0.00000)]) # raul - 23
#    angles.append([float(-0.00873), float(-0.25), float(-0.13962), float(0.00000), float(0.00000)]) # webots
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(1.20000)])
    return jointCodes, angles, times

#CIRCLE_STRAFE_COUNTER_CLOCKWISE = mirrorChoreographMove(*CIRCLE_STRAFE_CLOCKWISE)

@chorwrap
def CIRCLE_STRAFE_COUNTER_CLOCKWISE():
    jointCodes = list()
    angles = list()
    times = list()
    suspend = 1.20000

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.00000), float(-0.09250), float(-0.11868), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.08727), float(-0.00698), float(-0.00698), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.01745), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHand")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.08727), float(-0.10996), float(-0.10996), float(0.12217), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LHipRoll")
    #angles.append([float(0.00873), float(0.2), float(0.13962), float(0.00000), float(0.00000)]) # OLD cech + maldini
    #angles.append([float(0.00873), float(0.19), float(0.13962), float(0.00000), float(0.00000)]) # OLD gerrard
#    angles.append([float(0.00873), float(0.16), float(0.13962), float(0.00000), float(0.00000)]) # cech elipse...
    angles.append([float(0.00873), float(0.2), float(0.13962), float(0.00000), float(0.00000)]) # raul
#    angles.append([float(0.00873), float(0.25), float(0.13962), float(0.00000), float(0.00000)]) # webots
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180), float(0.26180), float(0.26180), float(0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333), float(suspend)])
    return jointCodes, angles, times

@chorwrap
def CIRCLE_STRAFER_INIT_POSE():
    jointCodes = list()
    angles = list()
    times = list()
    DT = 1.0 # 0.4

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("LHand")
    angles.append([float(-1.00000)])
    times.append([float(DT)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.12217)])
    times.append([float(DT)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.30892)])
    times.append([float(DT)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(-0.30892)])
    times.append([float(DT)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266)])
    times.append([float(DT)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180)])
    times.append([float(DT)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("RHand")
    angles.append([float(-1.00000)])
    times.append([float(DT)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.12217)])
    times.append([float(DT)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000)])
    times.append([float(DT)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266)])
    times.append([float(DT)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180)])
    times.append([float(DT)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000)])
    times.append([float(0.66667)])
    return jointCodes, angles, times

@chorwrap
def TURN_CW():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.22515), float(0.12217)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.00698), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.22515), float(-0.26529)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.22515), float(-0.26529)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(1.04719)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHand")
    angles.append([float(-1.00000), float(-1.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHand")
    angles.append([float(-1.00000), float(-1.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.22340), float(0.12217)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHipRoll")
    angles.append([float(-0.15010), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(1.04719)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])
    return jointCodes, angles, times

@chorwrap
def TURN_CCW():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.22515), float(0.12217)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.15010), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.22515), float(-0.26529)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHipYawPitch")
    angles.append([float(0.22515), float(-0.26529)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHand")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.22340), float(0.12217)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RHipRoll")
    angles.append([float(-0.00698), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])
    return jointCodes, angles, times

@chorwrap
def TO_BELLY_FROM_LEAP_RIGHT():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(-0.26696)])
    times.append([float(0.90000)])

    jointCodes.append("HeadYaw")
    angles.append([float(-0.00618)])
    times.append([float(0.90000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(0.55987), float(-0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(-0.14109), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000), float(0.00000)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(1.73184), float(1.64134)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LHand")
    angles.append([float(-0.99852), float(-0.99779)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.61969), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.15958), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.05518), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.01376), float(0.00000)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(-0.09250), float(-1.55092)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.00000), float(0.39880)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.01683), float(-0.01078)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.77625), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.07828), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.20406), float(0.20713)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.63964), float(0.64731)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RHand")
    angles.append([float(-0.99816), float(-0.99779)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.06899), float(-0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.21787), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00004)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(-1.55237), float(-1.54930)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.08595), float(-0.08134)])
    times.append([float(0.90000), float(10.20000)])

    jointCodes.append("RWristYaw")
    angles.append([float(-0.00004), float(-0.00004)])
    times.append([float(0.90000), float(10.20000)])

    return jointCodes, angles, times

TO_BELLY_FROM_LEAP_LEFT = mirrorChoreographMove(*TO_BELLY_FROM_LEAP_RIGHT)

@chorwrap
def GOALIE_LEAP_RIGHT_SAFE():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(0.00609), float(-0.00004), float(-0.00004)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("HeadYaw")
    angles.append([float(0.00149), float(-0.00004), float(-0.00004)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(-0.67807), float(0.55833), float(0.56907)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(-0.25767), float(-0.12575), float(-0.13342)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(-0.69793), float(-1.25017), float(-1.26532)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(-0.57376), float(-0.55228), float(-0.54624)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LHand")
    angles.append([float(-0.99052), float(-0.25001), float(-0.25001)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LHipPitch")
    angles.append([float(-0.38806), float(-1.34067), float(-0.63197)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LHipRoll")
    angles.append([float(-0.39420), float(-0.32977), float(-0.26841)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.06899), float(0.00004), float(0.00004)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LKneePitch")
    angles.append([float(1.17193), float(0.00456), float(0.00303)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(1.28392), float(0.73014), float(0.71212)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.10274), float(0.00868), float(0.00868)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("LWristYaw")
    angles.append([float(-0.02919), float(-1.25783), float(-1.25840)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(-1.22173), float(-1.22169), float(0.78535)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(-0.10734), float(-0.00609), float(0.07828)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(1.54785), float(1.57086), float(0.20100)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(1.41124), float(1.41431), float(0.63964)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RHand")
    angles.append([float(-0.99234), float(-1.00000), float(-1.00000)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RHipPitch")
    angles.append([float(-1.17969), float(-1.30087), float(0.07973)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RHipRoll")
    angles.append([float(-0.77463), float(-0.12575), float(0.20867)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RKneePitch")
    angles.append([float(2.19059), float(2.18906), float(0.00464)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(1.55398), float(0.47251), float(-1.55390)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-1.36223), float(-1.22417), float(-0.09975)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    jointCodes.append("RWristYaw")
    angles.append([float(2.35772), float(1.25659), float(1.25659)])
    times.append([float(0.80000), float(1.50000), float(2.20000)])

    return jointCodes, angles, times

@chorwrap
def GOALIE_LEAP_LEFT_SAFE():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(0.00609), float(0.00609), float(0.00609)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("HeadYaw")
    angles.append([float(0.00149), float(0.00149), float(0.00149)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(-1.22173), float(-1.22168), float(0.78537)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.10474), float(0.00608), float(-0.07829)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(-1.54786), float(-1.56215), float(-0.20101)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(-1.41123), float(-1.41429), float(-0.63962)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LHand")
    angles.append([float(-0.99991), float(-0.99991), float(-0.99991)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LHipPitch")
    angles.append([float(-1.17970), float(-1.30089), float(0.07971)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.77462), float(0.12573), float(-0.20868)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.06899), float(-0.06899), float(-0.06899)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LKneePitch")
    angles.append([float(2.19061), float(2.18907), float(0.00466)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(1.55400), float(0.47253), float(-1.55389)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(1.36225), float(1.22419), float(0.09976)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("LWristYaw")
    angles.append([float(-1.82378), float(-1.82378), float(-1.82378)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(-0.67808), float(0.55832), float(0.56906)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.25766), float(0.12573), float(0.13340)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.69792), float(1.25016), float(1.26530)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.57377), float(0.55229), float(0.54625)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RHand")
    angles.append([float(-0.99991), float(-0.99991), float(-0.99991)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.38805), float(-1.34066), float(-0.63195)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.39418), float(0.32976), float(0.26840)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RKneePitch")
    angles.append([float(1.17192), float(0.00455), float(0.00301)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(1.28390), float(0.73013), float(0.71211)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.10272), float(-0.00867), float(-0.00867)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    jointCodes.append("RWristYaw")
    angles.append([float(1.82379), float(1.82379), float(1.82379)])
    times.append([float(0.70000), float(1.40000), float(2.10000)])

    return jointCodes, angles, times
