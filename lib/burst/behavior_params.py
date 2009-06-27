from burst_consts import LEFT, RIGHT, DEG_TO_RAD
from burst.world import World
from burst_util import (polar2cart, cart2polar)

#===============================================================================
# This file contains the behavior parameters. The default values are for the
# Webots simulation.
#
# Note: Some values are overridden by the personalization file (per-robot file).
#===============================================================================

### Ball position relative to robot
# BALL_IN_KICKING_AREA - ball is ready to be kicked
# BALL_BETWEEN_LEGS - ball between legs
# BALL_FRONT_NERA - ball in front (between minimum and maximum KICK_Y)
# BALL_FRONT_FAR -
# BALL_SIDE_NEAR - ball on side (between minimum and maximum KICK_X)
# BALL_SIDE_FAR -
# BALL_DIAGONAL - ball diagonal (else...)
###
(BALL_IN_KICKING_AREA,
 BALL_BETWEEN_LEGS,
 BALL_FRONT_NEAR,
 BALL_FRONT_FAR,
 BALL_SIDE_NEAR,
 BALL_SIDE_FAR,
 BALL_DIAGONAL
 ) = range(7)

(MOVE_FORWARD,
 MOVE_ARC,
 MOVE_TURN,
 MOVE_SIDEWAYS,
 MOVE_CIRCLE_STRAFE,
 MOVE_KICK
 ) = range(6)

MOVEMENT_PERCENTAGE_FORWARD = 0.9
MOVEMENT_PERCENTAGE_SIDEWAYS = 0.9
MOVEMENT_PERCENTAGE_TURN = 0.9

## Kicks
# Kick consts (Measurements acquired via headTrackingTester)
# First value is for LEFT leg, second for RIGHT leg
KICK_X_MIN = [14, 14]
KICK_X_MAX = [18, 18]
KICK_Y_MIN = [4.0, -4.0]
KICK_Y_MAX = [6.0, -6.5]

KICK_X_OPT = ((KICK_X_MAX[LEFT]+KICK_X_MIN[LEFT])/2, (KICK_X_MAX[RIGHT]+KICK_X_MIN[RIGHT])/2)
KICK_Y_OPT = ((KICK_Y_MAX[LEFT]+KICK_Y_MIN[LEFT])/2, (KICK_Y_MAX[RIGHT]+KICK_Y_MIN[RIGHT])/2)

KICK_TURN_ANGLE = 45 * DEG_TO_RAD
KICK_SIDEWAYS_DISTANCE = 10.0
MAX_FORWARD_WALK = 200 # 200cm is the farthest we can stably go without stopping
MAX_SIDESTEP_WALK = 20 # 20 cm is the farthest we go on side-stepping without stopping

def calcTarget(distSmoothed, bearing):
    target_x, target_y = polar2cart(distSmoothed, bearing)
    return calcTargetXY(target_x, target_y)

def calcTargetXY(target_x, target_y):
    print "target_x: %3.3fcm, target_y: %3.3fcm" % (target_x, target_y)

    # determine kicking leg
    side = target_y < 0 # 0 = LEFT, 1 = RIGHT
    print "Designated kick leg: %s" % (side==LEFT and "LEFT" or "RIGHT")

    # calculate optimal kicking point
    kp_x, kp_y = target_x - KICK_X_OPT[side], target_y - KICK_Y_OPT[side]
    kp_dist, kp_bearing = cart2polar(kp_x, kp_y)
    print "kp_x: %3.3fcm   kp_y: %3.3fcm" % (kp_x, kp_y)
    print "kp_dist: %3.3fcm   kp_bearing: %3.3f" % (kp_dist, kp_bearing)

    # ball location, as defined at behavior parameters (front, side, etc...)
    target_location = calcBallArea(target_x, target_y, side)
    print ('TARGET_IN_KICKING_AREA', 'TARGET_BETWEEN_LEGS', 'TARGET_FRONT_NEAR', 'TARGET_FRONT_FAR','TARGET_SIDE_NEAR', 'TARGET_SIDE_FAR', 'TARGET_DIAGONAL')[target_location]

    # by Vova - new kick TODO: use consts, add explanation of meaning, perhaps move inside adjusted_straight_kick (passing ball, of course)
    kick_side_offset = 1.1-1.2*(abs(target_y-KICK_Y_MIN[side])/7)
    return side, kp_x, kp_y, kp_dist, kp_bearing, target_location, kick_side_offset


def calcBallArea(ball_x, ball_y, side):
    if isInEllipse(ball_x, ball_y, side):
#    if (ball_x <= KICK_X_MAX[side]) and (abs(KICK_Y_MIN[side]) < abs(ball_y) <= abs(KICK_Y_MAX[side])): #KICK_X_MIN[side] <
        return BALL_IN_KICKING_AREA
    elif KICK_Y_MAX[RIGHT] < ball_y < KICK_Y_MAX[LEFT]:
        if ball_x <= KICK_X_MAX[side]:
            return BALL_BETWEEN_LEGS
        elif ball_x <= KICK_X_MAX[side]*3/2:
            return BALL_FRONT_NEAR
        else:
            return BALL_FRONT_FAR
    else: #if (ball_y > KICK_Y_MAX[LEFT] or ball_y < KICK_Y_MAX[RIGHT]):
        if ball_x <= KICK_X_MAX[side]:
            if abs(ball_y) <= abs(KICK_Y_MAX[side])*10:
                return BALL_SIDE_NEAR
            else:
                return BALL_SIDE_FAR
        else: #ball_x > KICK_X_MAX[side]
            return BALL_DIAGONAL

def isInEllipse(ball_x, ball_y, side, margin=0):
    #TODO: check if margin is legit
    radius = (KICK_Y_MAX[side]-KICK_Y_MIN[side])/2
    y_center = (KICK_Y_MAX[side]+KICK_Y_MIN[side])/2
    a = radius + margin
    b = KICK_X_MAX[side]-KICK_X_MIN[side]
    if ((ball_y-y_center)**2)/(a**2)+((ball_x-KICK_X_MIN[side])**2)/(b**2)<=1:
        print "IN ELLIPSE: ball close enough"
        return True
    print "OUT OF ELLIPSE: ball too far"
    return False

delta_table = [(-0.55,4),(-0.44,3.5),(-0.38,3),(-0.31,2.5),(-0.24,2),(-0.14,1.5),(-0.09,1),(-0.03,0.5),(0,0),(0.07,-0.5),(0.1,-1),(0.12,-1.5),(0.19,-2),(0.24,-2.5),(0.33,-3),(0.42,-3.5),(0.52,-4)]

def getKickingType(self, goal_bearing, ball_y, side, margin=0):
    def lookUpDelta(goal_bearing):
        for i in range(len(delta_table)):
            if goal_bearing == delta_table[i][0]:
                return delta_table[i][1]
            if goal_bearing < delta_table[i][0]:
                if i==0:
                    return None
                return (delta_table[i-1][1] - 0.5*(delta_table[i][0]-goal_bearing)/(delta_table[i][0]-delta_table[i-1][0]))
        return None

    print "Starting to think diagonally"
    delta_y = lookUpDelta(goal_bearing)
    if delta_y == None:
        print "DIAGONAL KICK NOT VIABLE!"
        return None
    foot_y = delta_y + ball_y
    print "ball is at ", ball_y, ", delta is ", delta_y, ", so foot needs to be at ", foot_y
    
    # Alon: set default kick_parameter, since your if's didn't cover all bases.
    kick_parameter = 0.5

    if side == LEFT: 
        if foot_y >= KICK_Y_MIN[LEFT]-margin and foot_y <= KICK_Y_MAX[LEFT]+margin:
            if foot_y < KICK_Y_MIN[LEFT]:
                kick_parameter = 1.0
            elif foot_y > KICK_Y_MAX[LEFT]:
                kick_parameter = 0.0
            else: #foot_y >= KICK_Y_MIN[LEFT] and foot_y <= KICK_Y_MAX[LEFT]:
                kick_parameter = 1 - (foot_y - KICK_Y_MIN[LEFT])/(KICK_Y_MAX[LEFT] - KICK_Y_MIN[LEFT])
    else: #if side == RIGHT:
        if foot_y >= KICK_Y_MAX[RIGHT]-margin and foot_y <= KICK_Y_MIN[RIGHT]+margin:
            if foot_y > KICK_Y_MIN[RIGHT]:
                kick_parameter = 1.0
            elif foot_y < KICK_Y_MAX[RIGHT]:
                kick_parameter = 0.0
            else: #foot_y >= KICK_Y_MIN[RIGHT] and foot_y <= KICK_Y_MAX[RIGHT]:
                kick_parameter = (foot_y - KICK_Y_MAX[RIGHT])/(KICK_Y_MIN[RIGHT] - KICK_Y_MAX[RIGHT])
    
    print "kick_parameter: ", kick_parameter
    return kick_parameter
