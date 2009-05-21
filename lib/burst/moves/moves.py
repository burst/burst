
#constants file to store all our sweet ass-moves for the Nao # Marvelous XKCD reference!
#import MotionConstants
from burst.consts import DEG_TO_RAD
from ..world import World
from .. import walkparameters; WalkParameters = walkparameters.WalkParameters

# array with names of attributes of this module that can be run with executeMove
# in the naojoints utility (burst/bin/naojoints.py)
NAOJOINTS_EXECUTE_MOVE_MOVES = "INITIAL_POS SIT_POS ZERO_POS STAND".split()

def getMoveTime(move):
    totalTime = 0.0
    for target in move:
        if len(target) == 6:
            totalTime += target[4]
        elif len(target) == 3:
            totalTime += target[1]
    return totalTime

'''
    Angles:
        LEFT: ShoulderPitch,ShoulderRoll,ElbowYaw,ElbowRoll
        LEFT: HipYawPitch,HipRoll,HipPitch,KneePitch,AnklePitch,AnkleRoll
        RIGHT: HipYawPitch,-HipRoll,HipPitch,KneePitch,AnklePitch,-AnkleRoll
        RIGHT: ShoulderPitch,ShoulderRoll,ElbowYaw,ElbowRoll
    Note:
        To convert symmetric left/right movements, yaw and roll should also be * -1 - see mirrorChoreographMove
'''

INITIAL_POS = (((90.,20.,-80.,-45.),
                (0.,0.,-25.,40.,-20.,0.),
                (0.,0.,-25.,40.,-20.,0.),
                ((90.,-20.,80.,45.)),4.0),)

#Angles measured pretty exactly from the robot w/gains off.
#might want to make them even different if we suspect the motors are weakening
SIT_POS = (((0.,90.,0.,0.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (0.,-90.,0.,0.),3.0),
           ((90.,0.,-65.,-57.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (90.,0.,65.,57.),1.5))

ZERO_POS = (((0.,0.,0.,0.),(0.,0.,0.,0.,0.,0.),(0.,0.,0.,0.,0.,0.),(0.,0.,0.,0.),4.0),)
PENALIZED_POS = INITIAL_POS

STAND = (((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),)

SET_POS = INITIAL_POS

READY_POS = INITIAL_POS


# HEAD SCANS
CAM_MAXIMUM_V = 30. * DEG_TO_RAD # NOTE: should have been 45 according to specs
CAM_MINIMUM_V = -45. * DEG_TO_RAD
CAM_MAXIMUM_H = 90. * DEG_TO_RAD # TODO: check if can be changed to 120 (mainly for goalie, via DCM)
CAM_FRONTAL_H = CAM_MAXIMUM_H * 2 / 3 # can be useful to scan front area and not entire possible area

BOTTOM_CENTER_H_MAX_V_FAR = (0., -CAM_MAXIMUM_V) # minimize top part seen - allow keeper to see top of goal bar
BOTTOM_CENTER_H_MAX_V_CLOSE = (0., -CAM_MAXIMUM_V * 3 / 2) # maximize top part seen - better when close to opponent goal
BOTTOM_CENTER_H_MIN_V = (0., CAM_MAXIMUM_V) # maximize top part seen - better when close to opponent goal

# Start from bottom part (closer is probably more important), continue with middle, finish with top
# TODO: check what's the fastest time for scanning where ball/goal is still detected (can save lots of time)
BOTTOM_FRONT_SCAN = (
    (BOTTOM_CENTER_H_MAX_V_FAR, 0.2),
    ((-CAM_FRONTAL_H, CAM_MAXIMUM_V), 0.2),
    ((CAM_FRONTAL_H, CAM_MAXIMUM_V), 3.0),
    ((CAM_FRONTAL_H, 0), 0.2),
    ((-CAM_FRONTAL_H, 0), 3.0),
    ((-CAM_FRONTAL_H, -CAM_MAXIMUM_V), 0.2),
    ((CAM_FRONTAL_H, -CAM_MAXIMUM_V), 4.0),
    ((CAM_FRONTAL_H, CAM_MINIMUM_V), 0.2),
    ((-CAM_FRONTAL_H, CAM_MINIMUM_V), 3.0),
    (BOTTOM_CENTER_H_MAX_V_FAR, 0.2),
    )

BOTTOM_QUICK_SCAN = (
    (BOTTOM_CENTER_H_MAX_V_FAR, 0.2),
    ((0.0, CAM_MAXIMUM_V), 1.0),
    ((0.0, CAM_MINIMUM_V), 2.0),
    (BOTTOM_CENTER_H_MAX_V_FAR, 0.2),
    )

BOTTOM_INIT_FAR = ((BOTTOM_CENTER_H_MAX_V_FAR, 0.5),)
BOTTOM_INIT_CLOSE = ((BOTTOM_CENTER_H_MAX_V_CLOSE, 0.5),)
BOTTOM_CENTER_H_MIN_V = ((BOTTOM_CENTER_H_MIN_V, 0.5),)

LOC_PANS = (
    (( 65.0, 10.0),1.5),
    ((65.,-25.),1.0),
    ((-65.,-25.),2.5),
    ((-65.0, 10.0) ,1.),
    (( 0.0, 10.0),1.5),)

SCAN_BALL= (
    (( 65.0, 20.0),1.0),
    ((65.,-30.),0.75),
    ((-65.,-30.),2.0),
    ((-65.0, 20.0) ,0.75),
    (( 0.0, 20.0),1.0),)

#ZERO_HEADS = (((0.0,0.0),1.0),)
#NEUT_HEADS = (((0.,20.),2.0),)
#PENALIZED_HEADS = (((0.0,25.0),0.5),)

# WALKS
FASTEST_WALK_WEBOTS = WalkParameters([
           100.0 * DEG_TO_RAD, # 0 ShoulderMedian
           10.0 * DEG_TO_RAD,    # 1 ShoulderAmplitude
           30.0 * DEG_TO_RAD,    # 2 ElbowMedian 
           10.0 * DEG_TO_RAD,    # 3 ElbowAmplitude 
           2.5,                  # 4 LHipRoll(degrees) 
           -2.5,                 # 5 RHipRoll(degrees)
           0.23,                 # 6 HipHeight(meters)
           3.0,                  # 7 TorsoYOrientation(degrees)
           0.07,                 # 8 StepLength
           0.042,                 # 9 StepHeight
           0.06,                 # 10 StepSide (was 0.02)
           0.3,                  # 11 MaxTurn
           0.015,                # 12 ZmpOffsetX
           0.018,                # 13 ZmpOffsetY 
           54])                  # 14 20ms count per step

FAST_WALK_WEBOTS = WalkParameters([
           110.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           90.0 * DEG_TO_RAD,  # ElbowMedian 
           0.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) (2.5 original)
           -4.5,                  # RHipRoll(degrees) (-2.5 original)
           0.23,                  # HipHeight(meters) MAX
           0.0,                   # TorsoYOrientation(degrees)
           0.04,                  # StepLength MAX
           0.025,                  # StepHeight MAX
           0.02,                  # StepSide
           0.3,                   # MaxTurn
           0.06,                  # ZmpOffsetX MAX
           0.016,                 # ZmpOffsetY 
           18])

FASTER_WALK = WalkParameters([
           110.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           90.0 * DEG_TO_RAD,  # ElbowMedian 
           0.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) (2.5 original)
           -4.5,                  # RHipRoll(degrees) (-2.5 original)
           0.23,                  # HipHeight(meters)
           0.0,                   # TorsoYOrientation(degrees)
           0.04,                  # StepLength
           0.02,                  # StepHeight
           0.02,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.016,                 # ZmpOffsetY 
           18])#,                    # 20ms count per step
           #,0.68]                  # Angle 0.68

FAST_WALK = WalkParameters([
           100.0 * DEG_TO_RAD, # 0 ShoulderMedian
           10.0 * DEG_TO_RAD,    # 1 ShoulderAmplitude
           30.0 * DEG_TO_RAD,    # 2 ElbowMedian 
           10.0 * DEG_TO_RAD,    # 3 ElbowAmplitude 
           3.5,                  # 4 LHipRoll(degrees) 
           -3.5,                 # 5 RHipRoll(degrees)
           0.23,                 # 6 HipHeight(meters)
           3.0,                  # 7 TorsoYOrientation(degrees)
           0.04,                 # 8 StepLength
           0.02,                 # 9 StepHeight
           0.02,                 # 10 StepSide
           0.3,                  # 11 MaxTurn
           0.015,                # 12 ZmpOffsetX
           0.018,                # 13 ZmpOffsetY 
           # Not walk parameters proper.
           25])                   # 15 20ms count per step

STD_WALK = WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           10.0 * DEG_TO_RAD,  # ElbowAmplitude 
           2.5,                   # LHipRoll(degrees) 
           -2.5,                  # RHipRoll(degrees)
           0.23,                  # HipHeight(meters)
           0.0,                   # TorsoYOrientation(degrees)
           0.04,                  # StepLength
           0.02,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.018,                 # ZmpOffsetY 
           25])                    # 20ms count per step

SLOW_WALK1 = WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           10.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4,                   # LHipRoll(degrees) 
           -4.5,                  # RHipRoll(degrees)
           0.19,                  # HipHeight(meters)
           5.0,                   # TorsoYOrientation(degrees)
           0.055,                  # StepLength
           0.042,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.015,                  # ZmpOffsetX
           0.00,                  # ZmpOffsetY 
           100])                    # 20ms count per step

SLOW_WALK = WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           15.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           10.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) 
           -4.5,                  # RHipRoll(degrees)
           0.22,                  # HipHeight(meters)
           3.4,                   # TorsoYOrientation(degrees)
           0.070,                  # StepLength
           0.043,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.00,                  # ZmpOffsetY 
           80])                    # 20ms count per step

# Alon is looking for a walk that DOESN'T FALL!!!

KICKER_WALK = WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           15.0 * DEG_TO_RAD,      # ShoulderAmplitude
           30.0 * DEG_TO_RAD,      # ElbowMedian 
           10.0 * DEG_TO_RAD,      # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) 
           -4.5,                  # RHipRoll(degrees)
           0.22,                  # HipHeight(meters)
           3.4,                   # TorsoYOrientation(degrees)
           0.070,                  # StepLength
           0.043,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.00,                  # ZmpOffsetY 
           120])                    # 20ms count per step

if World.connected_to_nao:
    FASTEST_WALK = SLOW_WALK
else:
    FASTEST_WALK = FASTEST_WALK_WEBOTS

#KICKS

KICK_STR_OFFSET_FROM_BODY = 4 # in cm

KICK_STR_DISTANCE = 17 # in cm


KICK_STRAIGHT = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #kick the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-55.,60.,-5.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),.08),
    #unkick the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),.08),
    #put the left leg back down the middle
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0))

SHPAGAT = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0))


SIDE_KICK_LEFT= (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #Lift left leg    
    ((80.,40.,-50.,-70.),
     (0.,20.,-50.,60.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #Ready
    ((80.,40.,-50.,-70.),
     (0.,15.,-50.,60.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #Kick
    ((80.,40.,-50.,-70.),
     (0.,50.,-50.,60.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.15),
    #Lift left leg    
    ((80.,40.,-50.,-70.),
     (0.,20.,-50.,60.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),1.0))

SIDE_KICK_RIGHT= (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the left
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-10.,20.,-10.,20.),
     (80.,-40.,50.,70.),0.8),
    #lift the right leg
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-50.,60.,-10.,20.),
     (80.,-40.,50.,70.),1.0),    
    #Ready
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-15.,-50.,60.,-10.,20.),
     (80.,-40.,50.,70.),1.0),    
    #Kick
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-50.,-50.,60.,-10.,20.),
     (80.,-40.,50.,70.),0.15),    
    #lift the right leg
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-50.,60.,-10.,20.),
     (80.,-40.,50.,70.),1.0),    
    #swing to the left
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-10.,20.,-10.,20.),
     (80.,-40.,50.,70.),0.8),
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),1.0))


HALF_KICK = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),1.0),
    #Get ready
    ((80.,40.,-50.,-70.),
     (0.,30.,-20.,120.,-40.,0.),
     (-10.,30.,-10.,10.,-10.,-20.),
     (80.,-40.,50.,70.),1.2))

NEW_MOVE = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),1.0),
    #left
    ((80.,40.,-50.,-70.),
     (0.,0.,-20.,20.,0.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),1.0),
    #right
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-20.,20.,0.,0.),
     (80.,-40.,50.,70.),1.0))

KICK_OFF = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),1.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-50.,60.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),1.0),
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),1.0))


ALMOST_KICK = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #Get ready
    ((80.,40.,-50.,-70.),
     (0.,30.,-20.,120.,-40.,0.),
     (-10.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #Kick
    ((80.,40.,-50.,-70.),
     (0.,20.,-70.,60.,-30.,0.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.17),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0))

GREAT_KICK_LEFT = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.8),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,80.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),1.0),
    #Get ready
    ((80.,40.,-50.,-70.),
     (-10.,30.,-20.,120.,-40.,0.),
     (0.,30.,-10.,10.,-10.,-20.),
     (80.,-40.,50.,70.),1.2),
    #Kick
    ((80.,40.,-50.,-70.),
     (0.,20.,-70.,60.,-30.,0.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.18),
    #make leg go further away
    ((80.,40.,-50.,-70.),
     (0.,20.,-50.,10.,120.,0.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),0.18),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0))

GREAT_KICK_RIGHT = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the left
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-10.,20.,-10.,20.),
     (80.,-40.,50.,70.),0.8),
    #lift the right leg
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-30.,80.,-30.,20.),
     (80.,-40.,50.,70.),1.0),
    #Get ready
    ((80.,40.,-50.,-70.),
     (0.,-30.,-10.,10.,-10.,20.),
     (-10.,-30.,-20.,120.,-40.,0.),
     (80.,-40.,50.,70.),1.2),
    #Kick
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-70.,60.,-30.,0.),
     (80.,-40.,50.,70.),0.18),
    #make leg go further away
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-50.,10.,120.,0.),
     (80.,-40.,50.,70.),0.18),
    #lift the right leg
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-30.,60.,-30.,20.),
     (80.,-40.,50.,70.),1.5),
    #swing to the left
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-10.,20.,-10.,20.),
     (80.,-40.,50.,70.),1.5),
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),1.0)
    )


KICK_A = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the right
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #lift the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #kick the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-55.,60.,-5.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),.05),
    #unkick the left leg
    ((80.,40.,-50.,-70.),
     (0.,20.,-30.,60.,-30.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),.08),
    #put the left leg back down the middle
    ((80.,40.,-50.,-70.),
     (0.,20.,-10.,20.,-10.,-20.),
     (0.,20.,-10.,20.,-10.,-20.),
     (80.,-40.,50.,70.),2.0),
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0))

KICK_STRAIGHT_RIGHT = (
    #Stand up more fully
    ((80.,40.,-50.,-70.),
     (0.,0.,-10.,20.,-10.,0.),
     (0.,0.,-10.,20.,-10.,0.),
     (80.,-40.,50.,70.),2.0),
    #swing to the left
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-10.,20.,-10.,20.),
     (80.,-40.,50.,70.),2.0),
    #lift the right leg
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-30.,60.,-30.,20.),
     (80.,-40.,50.,70.),2.0),
    #kick the right leg
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-55.,60.,-5.,20.),
     (80.,-40.,50.,70.),.08),
    #unkick the right leg
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-30.,60.,-30.,20.),
     (80.,-40.,50.,70.),.08),
    #put the right leg back down the middle
    ((80.,40.,-50.,-70.),
     (0.,-20.,-10.,20.,-10.,20.),
     (0.,-20.,-10.,20.,-10.,20.),
     (80.,-40.,50.,70.),2.0))


#HEAD SCANS - From nao-man
LOC_PANS = (
    (( 65.0, 10.0),1.5),
    ((65.,-25.),1.0),
    ((-65.,-25.),2.5),
    ((-65.0, 10.0) ,1.),
    (( 0.0, 10.0),1.5),)

SCAN_BALL= (
    (( 65.0, 20.0),1.0),
    ((65.,-30.),0.75),
    ((-65.,-30.),2.0),
    ((-65.0, 20.0) ,0.75),
    (( 0.0, 20.0),1.0),)

POST_SCAN = (
    ((65.,-25.),2.0),
    ((-65.,-25.),2.0))

PAN_LEFT = (
    (( 65.0, 20.0),2.0),
    ((0.0,20.),2.0))
PAN_RIGHT = (
    (( -65.0, 20.0),2.0),
    ((0.0,20.),2.0))

# STAND UPS
STAND_UP_FRONT = ( ((90,50,0,0),
                    (0,8,0,120,-65,0),
                    (0,0,8,120,-65,4),
                    (90,-50,0,0 ),1.0),

                   ((90,90,0,0),
                    (0,8,0,120,-65,0),
                    (0,0,8,120,-65,4),
                    (90,-90,0,0 ),1.0),

                   ((-90,90,0,0),
                    (0,8,0,120,-65,0),
                    (0,0,8,120,-65,4),
                    (-90,-90,0,0 ),0.5),

                   ((-90,0,0,0),
                    (0,8,0,120,-65,0),
                    (0,0,8,120,-65,4),
                    (-90,0,0,0 ),0.75),

                   ((-90,0,-90,0),
                    (0,8,0,120,-65,0),
                    (0,0,8,120,-65,4),
                    (-90,0,90,0 ),0.3),

                   ((-50,0,-90,-35),
                    (5,8,-90,120,-65,0),
                    (5,0,-90,120,-65,4),
                    (-50,0,90,35),2.0),

                   ((-10,0,-90,-95),
                    (-50,8,-90,60,-44,-39),
                    (-50,0,-90,60,-44,39),
                    (-10,0,90,95),1.3),

                   ((0,0,-90,-8),
                    (-50,8,-90,58,5,-31),
                    (-50,0,-90,58,5,31),
                    (0,0,90,8),1.7),

                   ((35,2,-14,-41),
                    (-55,5,-90,123,-17,-17),
                    (-55,-5,-90,123,-17,17),
                    (35,2,14,41),0.8),

                   ((64,7,-53,-74),
                    (-45,6,-61,124,-41,-6),
                    (-45,-6,-61,124,-41,6),
                    (64,-7,53,74),1.2),

                   ((93,10,-90,-80),
                    (0,0,-60,120,-60,0),
                    (0,0,-60,120,-60,0),
                    (93,-10,90,80),1.0),

                   ( INITIAL_POS[0][0],
                     INITIAL_POS[0][1],
                     INITIAL_POS[0][2],
                     INITIAL_POS[0][3],0.5))

STAND_UP_BACK = ( ((0,90,0,0),
                   (0,0,0,0,0,0),
                   (0,0,0,0,0,0),
                   (0,-90,0,0),1.0),

                  ((120,46,9,0),
                   (0,8,10,96,14,0),
                   (0,0,10,96,14,4),
                   (120,-46,-9,0), 1.0),

                  ((120,25,10,-95),
                   (-2,8,0,70,18,0),
                   (-2,0,0,70,18,4),
                   (120,-25,-10,95),0.7),

                  ((120,22,15,-30),
                   (-38,8,-90,96,14,0),
                   (-38, 0,-90, 96, 14, 4),
                   ( 120,-22,-15, 30), 0.7),


                  ((120,0,5,0),
                   (-38,31,-90,96,45,0),
                   (-38,-31,-90,96,45,4),
                   (120,0,-5,0), 1.0),

                  ((40,60,4,-28),
                   (-28,8,-49,126,-32,-22),
                   (-28,-31,-87,70,45,0),
                   (120,-33,-4,4),1.0),

                  ((42,28,5,-47),
                   (-49,-16,22,101,-70,-5),
                   (-49,-32,-89,61,39,-7),
                   (101,-15,-4,3),0.9),

                  ((42,28,4,-46),
                   (-23,11,-49,126,-70,6),
                   (-23,-17,-51,50,23,38),
                   (51,-50,0,26), 1.0),

                  ((42,28,4,-46),
                   (-23,21,-47,126,-70,5),
                   (-23,-1,-51,101,-33,15),
                   (51,-39,0,32), 0.5),

                  ((98,2,-72,-65),
                   (0,0,-50,120,-70,0),
                   (0,0,-50,120,-70,0),
                   (98,-2,72,65), 1.1),

                  ( INITIAL_POS[0][0],
                    INITIAL_POS[0][1],
                    INITIAL_POS[0][2],
                    INITIAL_POS[0][3],0.5))

