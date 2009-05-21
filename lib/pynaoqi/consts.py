
localization_vars = [
 '/BURST/Loc/Ball/XEst',
 '/BURST/Loc/Ball/XUncert',
 '/BURST/Loc/Ball/XVelocityEst',
 '/BURST/Loc/Ball/XVelocityUncert',
 '/BURST/Loc/Ball/YEst',
 '/BURST/Loc/Ball/YUncert',
 '/BURST/Loc/Ball/YVelocityEst',
 '/BURST/Loc/Ball/YVelocityUncert',
 '/BURST/Loc/Self/HEst',
 '/BURST/Loc/Self/HEstDeg',
 '/BURST/Loc/Self/HUncert',
 '/BURST/Loc/Self/HUncertDeg',
 '/BURST/Loc/Self/LastOdoDeltaF',
 '/BURST/Loc/Self/LastOdoDeltaL',
 '/BURST/Loc/Self/LastOdoDeltaR',
 '/BURST/Loc/Self/XEst',
 '/BURST/Loc/Self/XUncert',
 '/BURST/Loc/Self/YEst',
 '/BURST/Loc/Self/YUncert',
]

# All units in centimeters
FIELD_OUTER_LENGTH = 740
FIELD_OUTER_WIDTH = 540
FIELD_LENGTH = 605
FIELD_WIDTH = 405

# 0,0 is bottom left of outer field (so all values are positive).
# x points towards yellow goal, y is positive for up.
GOAL_LEN = 140.0
OUTER_X_BUFFER = 67.5
BGRP_X = OUTER_X_BUFFER
BGRP_Y = FIELD_OUTER_WIDTH / 2.0 + GOAL_LEN / 2.0
BGLP_X = OUTER_X_BUFFER
BGLP_Y = FIELD_OUTER_WIDTH / 2.0 - GOAL_LEN / 2.0
YGRP_X = OUTER_X_BUFFER + FIELD_LENGTH
YGRP_Y = FIELD_OUTER_WIDTH / 2.0 + GOAL_LEN / 2.0
YGLP_X = OUTER_X_BUFFER + FIELD_LENGTH
YGLP_Y = FIELD_OUTER_WIDTH / 2.0 - GOAL_LEN / 2.0

fol = FIELD_OUTER_LENGTH
fow = FIELD_OUTER_WIDTH
fl = FIELD_LENGTH
fw = FIELD_WIDTH

LOC_SCREEN_X_SIZE = 740.0
LOC_SCREEN_Y_SIZE = 540.0


