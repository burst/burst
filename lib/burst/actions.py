import burst
from burst.consts import *
import moves
import world

INITIAL_STIFFNESS = 0.85 # TODO: Check other stiffnessesm, as this might not be optimal.
INITIAL_HEAD_PITCH = -20.0 * DEG_TO_RAD

class Actions(object):

    def __init__(self, world):
        self._world = world
        self._motion = burst.getMotionProxy()

    def initPoseAndStiffness(self):
        self._motion.setBodyStiffness(1.0)
        self._motion.setBalanceMode(BALANCE_MODE_OFF) # needed?
        self._motion.gotoAngle('HeadPitch', INITIAL_HEAD_PITCH, 1.0, INTERPOLATION_SMOOTH)
        self.executeMove(moves.STAND)
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        
    def sitPoseAndRelax(self):
        self.clearFootsteps()
        self.executeMove(moves.SIT_POS)
        self._motion.setBodyStiffness(0)

    def changeHeadAngles(self, delta_yaw, delta_pitch):
        #self._motion.changeChainAngles("Head", [delta_yaw, delta_pitch])
        self._motion.post.gotoChainAngles("Head", [self._motion.getAngle("HeadYaw")+delta_yaw, self._motion.getAngle("HeadPitch")+delta_pitch], 0.1, INTERPOLATION_SMOOTH)

    def gotoHeadAngles(self, yaw, pitch):
        self._motion.gotoChainAngles("Head", [yaw, pitch], 0.1, INTERPOLATION_SMOOTH)

    def setHeadAngles(self, yaw, pitch):
        self._motion.setChainAngles("Head", [yaw, pitch])

    def getAngle(self, joint_name):
        return self._motion.getAngle(joint_name)
    
    def kick(self):
        self.executeMove(moves.ALMOST_KICK)
    
    def turn(self, delta_theta):
        if self._world.robot.isWalkingActive or self._world.robot.isTurningActive:
            print "Still walking/turning, can't turn for now"
            return
        print "delta_theta: %f" % delta_theta
        
        self._world.robot.isTurningActive = True
        
        self._motion.setBodyStiffness(INITIAL_STIFFNESS)
        self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)

        # just turn
        self._motion.addTurn(delta_theta, 150) #25
        
        self._world.robot.turnID = self._motion.post.walk()
        print "self._world.robot.turnID: %f" % self._world.robot.turnID
        
    
    def changeLocation(self, delta_x, delta_y, delta_theta):
        if self._world.robot.isWalkingActive or self._world.robot.isTurningActive:
            print "Still walking/turning, can't change location for now"
            return
        
        # just turn
        if delta_theta != 0:
            self.turn(delta_theta)
        else:
            self._world.robot.isWalkingActive = True
            
            self._motion.setBodyStiffness(INITIAL_STIFFNESS)
            self._motion.setSupportMode(SUPPORT_MODE_DOUBLE_LEFT)
            
            # TODO
            #if self._world.ball.dist > 40:
                #fast walk
            #else:
                #slow walk
            
            distance = delta_x / 100 # convert cm to meter
            
            param = moves.SLOW_WALK # FASTER_WALK / FAST_WALK
    
            (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude,
                LHipRoll, RHipRoll, HipHeight, TorsoYOrientation,
                StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY) = param[:14]
    
            self._motion.setWalkArmsConfig( ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude )
            self._motion.setWalkArmsEnable(True)
    
            # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
            self._motion.setWalkExtraConfig( LHipRoll, RHipRoll, HipHeight, TorsoYOrientation )
    
            self._motion.setWalkConfig( StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY )
    
            if len(param) == 16:
		print "StepLength: %f distance: %f" % (StepLength, distance)
                self._motion.addWalkStraight( StepLength*2,150 ) # param[14]
                self._motion.addWalkStraight( distance-StepLength*2, param[15] ) # param[14]
            elif len(param) == 17:
                self._motion.addWalkArc( distance, param[16], param[15] ) # param[14]
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
        self._world.robot.walkID = self._motion.post.walk()
        print "self._world.robot.walkID: %f" % self._world.robot.walkID

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
        #if self._motion.getRemainingFootStepCount() > 0:
        self._motion.clearFootsteps()

