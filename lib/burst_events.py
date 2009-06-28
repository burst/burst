
# TODO: We'd might like to have the events fired in some predetermined order.
# TODO: We'd might like to have the events fired in some predetermined order.
# TODO: We'd might like to have the events fired in some predetermined order.

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
EVENT_ON_BELLY = counter; counter+=1
EVENT_ON_BACK = counter; counter+=1
EVENT_ON_LEFT_SIDE = counter; counter+=1
EVENT_ON_RIGHT_SIDE = counter; counter+=1
EVENT_PICKED_UP = counter; counter+=1
EVENT_BACK_ON_FEET = counter; counter+=1

# Sonar Obstacle Detection
EVENT_OBSTACLE_SEEN = counter; counter += 1
EVENT_OBSTACLE_LOST = counter; counter += 1
EVENT_OBSTACLE_IN_FRAME = counter; counter += 1

# Physical Events
EVENT_CHEST_BUTTON_PRESSED = counter; counter += 1
EVENT_CHEST_BUTTON_RELEASED = counter; counter += 1 # TODO: Remove?
EVENT_LEFT_BUMPER_PRESSED = counter; counter += 1
EVENT_RIGHT_BUMPER_PRESSED = counter; counter += 1

##### Vision events
EVENT_BALL_POSITION_CHANGED = counter; counter+=1
# Seen / Lost - raised once if the previous time step is different then the current.
EVENT_BALL_SEEN = counter; counter+=1
EVENT_BALL_LOST = counter; counter+=1
# Raised every time the ball is actually visible to the robot. (frame = vision device)
EVENT_BALL_IN_FRAME = counter; counter+=1
EVENT_BALL_BODY_INTERSECT_UPDATE = counter; counter+=1
BALL_MOVING_PENALTY = counter; counter+=1

# TODO - events for all goal posts and crossbars
EVENT_BGLP_POSITION_CHANGED = counter; counter+=1
EVENT_BGRP_POSITION_CHANGED = counter; counter+=1
EVENT_YGLP_POSITION_CHANGED = counter; counter+=1
EVENT_YGRP_POSITION_CHANGED = counter; counter+=1
EVENT_BGLP_IN_FRAME = counter; counter+=1
EVENT_BGRP_IN_FRAME = counter; counter+=1
EVENT_YGLP_IN_FRAME = counter; counter+=1
EVENT_YGRP_IN_FRAME = counter; counter+=1
EVENT_OUR_LP_POSITION_CHANGED = counter; counter+=1
EVENT_OUR_RP_POSITION_CHANGED = counter; counter+=1
EVENT_OPPOSING_LP_POSITION_CHANGED = counter; counter+=1
EVENT_OPPOSING_RP_POSITION_CHANGED = counter; counter+=1
EVENT_OUR_LP_IN_FRAME = counter; counter+=1
EVENT_OUR_RP_IN_FRAME = counter; counter+=1
EVENT_OPPOSING_LP_IN_FRAME = counter; counter+=1
EVENT_OPPOSING_RP_IN_FRAME = counter; counter+=1
# TODO - not SEEN, but IN_FRAME - be consistent!
EVENT_ALL_BLUE_GOAL_SEEN = counter; counter+=1
EVENT_ALL_YELLOW_GOAL_SEEN = counter; counter+=1
EVENT_ALL_BLUE_GOAL_IN_FRAME = counter; counter+=1
EVENT_ALL_YELLOW_GOAL_IN_FRAME = counter; counter+=1
EVENT_ALL_BLUE_GOAL_LOST = counter; counter+=1
EVENT_ALL_YELLOW_GOAL_LOST = counter; counter+=1
EVENT_ALL_OUR_GOAL_SEEN = counter; counter+=1
EVENT_ALL_OPPOSING_GOAL_SEEN = counter; counter+=1
EVENT_ALL_OUR_GOAL_LOST = counter; counter+=1
EVENT_ALL_OPPOSING_GOAL_LOST = counter; counter+=1
EVENT_ALL_OUR_GOAL_IN_FRAME = counter; counter+=1
EVENT_ALL_OPPOSING_GOAL_IN_FRAME = counter; counter+=1

# GameController Events:
# Goals:
EVENT_GOAL_SCORED = counter; counter += 1
EVENT_GOAL_SCORED_BY_MY_TEAM = counter; counter += 1
EVENT_GOAL_SCORED_BY_OPPOSING_TEAM = counter; counter += 1
# Penalties:
EVENT_I_GOT_PENALIZED = counter; counter += 1
EVENT_TEAMMATE_PENALIZED = counter; counter += 1
EVENT_OPPONENT_PENALIZED = counter; counter += 1
EVENT_I_GOT_UNPENALIZED = counter; counter += 1
EVENT_TEAMMATE_UNPENALIZED = counter; counter += 1
EVENT_OPPONENT_UNPENALIZED = counter; counter += 1
# In/Out of the game:
EVENT_I_AM_REENTERING_PLAY = counter; counter += 1
EVENT_I_AM_LEAVING_PLAY = counter; counter += 1
# Game-state changes:
EVENT_GAME_STATE_CHANGED = counter; counter += 1
EVENT_SWITCHED_TO_INITIAL_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_FROM_INITIAL_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_TO_READY_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_FROM_READY_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_TO_SET_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_FROM_SET_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_TO_PLAY_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_FROM_PLAY_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_TO_FINISH_GAME_STATE = counter; counter += 1
EVENT_SWITCHED_FROM_FINISH_GAME_STATE = counter; counter += 1

##### Location events
EVENT_WORLD_LOCATION_UPDATED = counter; counter += 1

##### Computed events
#EVENT_KP_CHANGED = counter; counter+=1

##### Time based events
# Please don't use these! it makes puppies cry.
EVENT_STEP = counter; counter+=1
EVENT_TIME_EVENT = counter; counter+=1

### Dcm events
# Pretty much debug code right now...
EVENT_MOTION_SEQUENCE_SENT = counter; counter+=1

################################################################################
LAST_EVENT_NUM = counter
################################################################################

# Util for debugging
the_items = [(event, name) for name, event in globals().items() if name == name.upper() and isinstance(event, int) and name[0] == 'E']
event_name_d = dict(the_items)
short_event_name_d = dict([(k, v.split('EVENT_')[1]) for k,v in the_items])
def event_name(event):
    return event_name_d.get(event, 'no such event %s' % event)
def short_event_name(event):
    return short_event_name_d.get(event, 'no such event %s' % event)

