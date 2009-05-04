import burst
from burst.consts import *
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
        
    def sitPoseAndRelax(self):
        self.executeMove(moves.SIT_POS)
        self._motion.setBodyStiffness(0)

    def changeHeadAngles(self, delta_yaw, delta_pitch):
        #self._motion.changeChainAngles("Head", [delta_yaw, delta_pitch])
        self._motion.gotoChainAngles("Head", [self._motion.getAngle("HeadYaw")+delta_yaw, self._motion.getAngle("HeadPitch")+delta_pitch], 0.1, INTERPOLATION_SMOOTH)
        
    def changeLocation(self, delta_x, delta_y):
        if self._motion.getRemainingFootStepCount() > 0:
            print "Still walking, won't change position for now"
            return
        
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)

        param = moves.FAST_WALK # FASTER_WALK / FAST_WALK

        # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
        self._motion.setWalkArmsConfig( param[0], param[1], param[2], param[3] )
        self._motion.setWalkArmsEnable(True)

        # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
        self._motion.setWalkExtraConfig( param[4], param[5], param[6], param[7] )

        # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
        self._motion.setWalkConfig( param[8], param[9], param[10], param[11], param[12], param[13] )

        if len(param) == 16:
            self._motion.addWalkStraight( param[14], param[15] )
        elif len(param) == 17:
            self._motion.addWalkArc( param[14], param[16], param[15] )
        else:
            print "ERROR: wrong number of parameters"
            return
          
        #motionProxy.addTurn( 0.3*5, 25 )
        #motionProxy.addWalkSideways(0.02*8, 25)
        #motionProxy.addWalkArc( 0.3*4, 0.3, 25 )
        #motionProxy.addWalkSideways(-0.02*8, 25)
        #motionProxy.addWalkStraight( -0.05*3, 25)
        #motionProxy.addTurn( 0.4*4, 80 )
        #motionProxy.addWalkSideways(-0.04*4, 80)
        self._motion.walk()   #Blocking Function


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

