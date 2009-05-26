from burst.consts import LEFT, RIGHT, DEG_TO_RAD

#===============================================================================
# This file contains the behavior parameters. The default values are for the
# Webots simulation.
# 
# Note: Some values are overridden by the personalization file (per-robot file). 
#===============================================================================

## Ball position relative to robot
(BALL_IN_KICKING_AREA,
 BALL_BETWEEN_LEGS
 ) = range(2)


## Kicks
# Kick consts (Measurements acquired via headTrackingTester)
# First value is for LEFT, second for RIGHT
KICK_X_MIN = (28.0,28.0)
KICK_X_MAX = (32.5,32.5)
KICK_Y_MIN = (6.0,-6.0)
KICK_Y_MAX = (13.0,-13.0)
    
KICK_X_OPT = ((KICK_X_MAX[LEFT]+KICK_X_MIN[LEFT])/2, (KICK_X_MAX[RIGHT]+KICK_X_MIN[RIGHT])/2)
KICK_Y_OPT = ((KICK_Y_MAX[LEFT]+KICK_Y_MIN[LEFT])/2, (KICK_Y_MAX[RIGHT]+KICK_Y_MIN[RIGHT])/2)

KICK_TURN_ANGLE = 45 * DEG_TO_RAD
KICK_SIDEWAYS_DISTANCE = 10.0

KICK_OFFSET_FROM_BALL = 12

