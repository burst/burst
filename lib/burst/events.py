
################################################################################
FIRST_EVENT_NUM = counter = 1
################################################################################

# I'm having a problem deciding how to sort this list. For now it is doubly sorted:
# major: by object
# minor: by order of computation (from basic to dependent)

# Base events

##### Movement, Joint movement.
EVENT_CHANGE_LOCATION_DONE = counter; counter+=1

EVENT_HEAD_MOVE_DONE = counter; counter+=1
EVENT_BODY_MOVE_DONE = counter; counter+=1

# Fall Detection
EVENT_FALLEN_DOWN = counter; counter+=1
EVENT_ON_BELLY = counter; counter+=1
EVENT_ON_BACK = counter; counter+=1

##### Vision events
EVENT_BALL_POSITION_CHANGED = counter; counter+=1
# Seen / Lost - raised once if the previous time step is different then the current.
EVENT_BALL_SEEN = counter; counter+=1
EVENT_BALL_LOST = counter; counter+=1
# Raised every time the ball is actually visible to the robot. (frame = vision device)
EVENT_BALL_IN_FRAME = counter; counter+=1
EVENT_BALL_BODY_X_ISECT_UPDATE = counter; counter+=1

# TODO - events for all goal posts and crossbars
EVENT_BGLP_POSITION_CHANGED = counter; counter+=1
EVENT_BGRP_POSITION_CHANGED = counter; counter+=1
EVENT_YGLP_POSITION_CHANGED = counter; counter+=1
EVENT_YGRP_POSITION_CHANGED = counter; counter+=1

EVENT_ALL_BLUE_GOAL_SEEN = counter; counter+=1
EVENT_ALL_YELLOW_GOAL_SEEN = counter; counter+=1

##### Computed events
EVENT_KP_CHANGED = counter; counter+=1

##### Time based events
# Please don't use these! it makes puppies cry.
EVENT_STEP = counter; counter+=1
EVENT_TIME_EVENT = counter; counter+=1

################################################################################
LAST_EVENT_NUM = counter
################################################################################

