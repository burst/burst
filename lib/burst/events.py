
################################################################################
FIRST_EVENT_NUM = counter = 1
################################################################################

# Base events
EVENT_WALK_DONE = counter; counter+=1
EVENT_TURN_DONE = counter; counter+=1
EVENT_BALL_POSITION_CHANGED = counter; counter+=1
EVENT_BALL_SEEN = counter; counter+=1
EVENT_BALL_LOST = counter; counter+=1
EVENT_BALL_IN_FRAME = counter; counter+=1
# TODO - events for all goal posts and crossbars
EVENT_BGLP_POSITION_CHANGED = counter; counter+=1
EVENT_BGRP_POSITION_CHANGED = counter; counter+=1
EVENT_YGLP_POSITION_CHANGED = counter; counter+=1
EVENT_YGRP_POSITION_CHANGED = counter; counter+=1

EVENT_ALL_BLUE_GOAL_SEEN = counter; counter+=1
EVENT_ALL_YELLOW_GOAL_SEEN = counter; counter+=1

# Computed events
EVENT_KP_CHANGED = counter; counter+=1

# Please don't use these! it makes puppies cry.
EVENT_STEP = counter; counter+=1
EVENT_TIME_EVENT = counter; counter+=1

################################################################################
LAST_EVENT_NUM = counter
################################################################################

