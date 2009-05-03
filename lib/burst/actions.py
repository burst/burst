import burst
from burst.consts import BALANCE_MODE_OFF, INTERPOLATION_SMOOTH, DEG_TO_RAD
import moves

INITIAL_STIFFNESS = 0.85
INITIAL_HEAD_PITCH = -20.0 * DEG_TO_RAD

class Actions(object):

    def __init__(self):
        self._motion = burst.getMotionProxy()

    def initPoseAndStiffness(self):
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setBalanceMode(BALANCE_MODE_OFF) # needed?
        self._motion.gotoAngle('HeadPitch', INITIAL_HEAD_PITCH, 1.0,
            INTERPOLATION_SMOOTH)
        self.executeMove(moves.STAND)

    def changeHeadAngles(self, delta_yaw, delta_pitch):
        #self._motion.changeChainAngles("Head", [delta_yaw, delta_pitch])
        self._motion.gotoChainAngles("Head", [self._motion.getAngle("HeadYaw")+delta_yaw, self._motion.getAngle("HeadPitch")+delta_pitch], 0.1, INTERPOLATION_SMOOTH)
        

    def executeMove(self, moves):
        """ Go through a list of body angles, works like northern bites code:
        moves is a list, each item contains:
         larm (tuple of 4), lleg (tuple of 6), rleg, rarm, interp_time, interp_type

        interp_type - 1 for SMOOTH, 0 for Linear
        interp_time - time in seconds for interpolation

        NOTE: currently this is SYNCHRONOUS - it takes at least
        sum(interp_time) to execute.
        """
        for move in moves:
            larm, lleg, rleg, rarm, interp_time, interp_type = move
            curangles = self._motion.getBodyAngles()
            joints = curangles[:2] + [x*DEG_TO_RAD for x in list(larm)
                    + [0.0, 0.0] + list(lleg) + list(rleg) + list(rarm)
                    + [0.0, 0.0]]
            self._motion.gotoBodyAngles(joints, interp_time, interp_type)
 
    def clearFootsteps(self):
        """ NOTE: USER BEWARE. We had problems with clearFootsteps """
        if self._motion.getRemainingFootStepCount() > 0:
            self._motion.clearFootsteps()

