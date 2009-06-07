from burst_consts import LEFT, RIGHT, DEG_TO_RAD
from burst.world import World

#===============================================================================
# This file contains the behavior parameters. The default values are for the
# Webots simulation.
# 
# Note: Some values are overridden by the personalization file (per-robot file). 
#===============================================================================

### Ball position relative to robot
# BALL_IN_KICKING_AREA - ball is ready to be kicked
# BALL_BETWEEN_LEGS - ball between legs
# BALL_FRONT - ball in front (between minimum and maximum KICK_Y)
# BALL_SIDE - ball on side (between minimum and maximum KICK_X)
# BALL_DIAGONAL - ball diagonal (else...)
###
(BALL_IN_KICKING_AREA,
 BALL_BETWEEN_LEGS,
 BALL_FRONT,
 BALL_SIDE_NEAR,
 BALL_SIDE_FAR,
 BALL_DIAGONAL
 ) = range(6)

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

def calcBallArea(ball_x, ball_y, side):
    if (ball_x <= KICK_X_MAX[side]) and (abs(KICK_Y_MIN[side]) < abs(ball_y) <= abs(KICK_Y_MAX[side])): #KICK_X_MIN[side] < 
        return BALL_IN_KICKING_AREA
    elif KICK_Y_MIN[RIGHT] < ball_y < KICK_Y_MIN[LEFT] and ball_x <= KICK_X_MAX[side]:
        return BALL_BETWEEN_LEGS
    elif KICK_Y_MAX[RIGHT] < ball_y < KICK_Y_MAX[LEFT]:
        return BALL_FRONT
    else: #if (ball_y > KICK_Y_MAX[LEFT] or ball_y < KICK_Y_MAX[RIGHT]):
        if ball_x <= KICK_X_MAX[side]:
            if abs(ball_y) <= abs(KICK_Y_MAX[side])*10:
                return BALL_SIDE_NEAR
            else:
                return BALL_SIDE_FAR
        else: #ball_x > KICK_X_MAX[side]
            return BALL_DIAGONAL
