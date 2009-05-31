from burst.consts import LEFT, RIGHT, DEG_TO_RAD
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
 BALL_SIDE,
 BALL_DIAGONAL
 ) = range(5)

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

KICK_OFFSET_FROM_BALL = 12

