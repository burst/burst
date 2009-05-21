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
    newJointCodes = [{'L':'R','R':'L'}.get(jc[0], jc[0]) + jc[1:] for jc in jointCodes]
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
    angles.append([float(-0.10742), float(0.01070), float(0.09046), float(0.02450)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("HeadYaw")
    angles.append([float(0.03064), float(-0.13350), float(-0.13964), float(-0.13810)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LAnklePitch")
    angles.append([float(-1.22173), float(-0.67960), float(0.56907), float(0.56907)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LAnkleRoll")
    angles.append([float(0.09975), float(-0.25307), float(-0.11961), float(-0.13342)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LElbowRoll")
    angles.append([float(-0.54453), float(-0.69026), float(-1.26551), float(-1.31460)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LElbowYaw")
    angles.append([float(-0.00771), float(-0.58143), float(-0.54615), float(-0.54768)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LHand")
    angles.append([float(-0.99197), float(-0.99125), float(-0.99161), float(-0.99088)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LHipPitch")
    angles.append([float(-0.73628), float(-0.39573), float(-1.32840), float(-0.63197)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LHipRoll")
    angles.append([float(-0.08433), float(-0.40187), float(-0.32363), float(-0.26841)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.21318), float(-0.13342), float(-0.04598), float(-0.06132)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LKneePitch")
    angles.append([float(2.17670), float(1.17960), float(0.01683), float(0.00303)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LShoulderPitch")
    angles.append([float(0.93723), float(1.27778), float(0.71173), float(0.71327)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LShoulderRoll")
    angles.append([float(0.05672), float(0.08740), float(0.00149), float(0.00000)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("LWristYaw")
    angles.append([float(-0.01998), float(-0.01998), float(-0.01845), float(-0.01998)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RAnklePitch")
    angles.append([float(-1.22173), float(-1.22173), float(-1.22173), float(0.78540)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RAnkleRoll")
    angles.append([float(-0.10120), float(-0.09507), float(-0.01070), float(0.07828)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RElbowRoll")
    angles.append([float(0.61671), float(0.94192), float(1.58160), float(0.20713)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RElbowYaw")
    angles.append([float(0.14262), float(1.40510), float(1.40050), float(0.63197)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RHand")
    angles.append([float(-0.99706), float(-0.99779), float(-0.99743), float(-0.99743)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RHipPitch")
    angles.append([float(-0.73329), float(-1.04470), float(-1.31161), float(0.07973)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RHipRoll")
    angles.append([float(0.09515), float(-0.67185), float(-0.12881), float(0.20867)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RKneePitch")
    angles.append([float(2.19213), float(2.20133), float(2.19980), float(0.00464)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RShoulderPitch")
    angles.append([float(0.96339), float(1.55552), float(0.50319), float(-1.57844)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.02765), float(-0.88669), float(-1.23951), float(-0.06294)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    
    jointCodes.append("RWristYaw")
    angles.append([float(-0.01692), float(-0.01692), float(-0.01385), float(-0.00925)])
    times.append([float(0.90000), float(1.50000), float(2.10000), float(2.90000)])
    return jointCodes, angles, times

GOALIE_LEAP_LEFT = mirrorChoreographMove(*GOALIE_LEAP_RIGHT)

@chorwrap
def CIRCLE_STRAFER():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.00000), float(-0.09250), float(-0.11868), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LHipRoll")
    angles.append([float(-0.08727), float(0.00698), float(0.00698), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(0.00000), float(0.00000), float(0.07505), float(-0.30892)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.01745), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180), float(0.26180), float(0.26180), float(0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RHand")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RHipPitch")
    angles.append([float(-0.08727), float(-0.10996), float(-0.10996), float(0.12217)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RHipRoll")
    angles.append([float(-0.00873), float(-0.21642), float(-0.21468), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266), float(0.87266), float(0.87266), float(0.87266)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180), float(-0.26180), float(-0.26180), float(-0.26180)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])

    jointCodes.append("RWristYaw")
    angles.append([float(0.00000), float(0.00000), float(0.00000), float(0.00000)])
    times.append([float(0.13333), float(0.46667), float(0.60000), float(0.73333)])
    return jointCodes, angles, times

@chorwrap
def CIRCLE_STRAFER_INIT_POSE():
    jointCodes = list()
    angles = list()
    times = list()

    jointCodes.append("HeadPitch")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("HeadYaw")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LAnklePitch")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LAnkleRoll")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LElbowRoll")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LElbowYaw")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LHand")
    angles.append([float(-1.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LHipPitch")
    angles.append([float(0.12217)])
    times.append([float(0.40000)])

    jointCodes.append("LHipRoll")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LHipYawPitch")
    angles.append([float(-0.30892)])
    times.append([float(0.40000)])

    jointCodes.append("LKneePitch")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("LShoulderPitch")
    angles.append([float(0.87266)])
    times.append([float(0.40000)])

    jointCodes.append("LShoulderRoll")
    angles.append([float(0.26180)])
    times.append([float(0.40000)])

    jointCodes.append("LWristYaw")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RAnklePitch")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RAnkleRoll")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RElbowRoll")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RElbowYaw")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RHand")
    angles.append([float(-1.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RHipPitch")
    angles.append([float(0.12217)])
    times.append([float(0.40000)])

    jointCodes.append("RHipRoll")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RKneePitch")
    angles.append([float(0.00000)])
    times.append([float(0.40000)])

    jointCodes.append("RShoulderPitch")
    angles.append([float(0.87266)])
    times.append([float(0.40000)])

    jointCodes.append("RShoulderRoll")
    angles.append([float(-0.26180)])
    times.append([float(0.40000)])

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
    angles.append([float(-0.15010), float(0.00000)])
    times.append([float(0.26667), float(0.46667)])

    jointCodes.append("LHipYawPitch")
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
    angles.append([float(-0.07155), float(0.00000)])
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
