import player_init # remove before inserting into code
import burst.behavior_params as params
from burst_consts import (LEFT, RIGHT)    
""" returns the correct foot and kicking type (if any) for a given goal angle and ball position relative to body.
    If a kick is not possible, it returns none as the kicking foot.
"""
delta_table = [(-0.55,4),(-0.44,3.5),(-0.38,3),(-0.31,2.5),(-0.24,2),(-0.14,1.5),(-0.09,1),(-0.03,0.5),(0,0),(0.07,-0.5),(0.1,-1),(0.12,-1.5),(0.19,-2),(0.24,-2.5),(0.33,-3),(0.42,-3.5),(0.52,-4)]

def getKickingType(goal_bearing, ball_y, margin):
    # checks left foot then right foot - can't be both    
    print "Starting to think iagonally"
    delta_y = lookUpDelta(goal_bearing)
    if delta_y == None:
        return None, None
    foot_y = delta_y + ball_y
    print "ball is at ", ball_y, ", delta is ", delta_y, ", so foot needs to be at ", foot_y
    print "Left foot range is [", params.KICK_Y_MIN[LEFT], ",", params.KICK_Y_MAX[LEFT], "]"
    print "Right foot range is [", params.KICK_Y_MAX[RIGHT], ",", params.KICK_Y_MIN[RIGHT], "]"
    if foot_y >= params.KICK_Y_MIN[LEFT] and foot_y <= params.KICK_Y_MAX[LEFT]:
        kick_parameter = 1 - (foot_y - params.KICK_Y_MIN[LEFT])/(params.KICK_Y_MAX[LEFT] - params.KICK_Y_MIN[LEFT])
        print "LEFT side, with parameter: ", kick_parameter         
        return LEFT, kick_parameter
    elif foot_y >= params.KICK_Y_MAX[RIGHT] and foot_y <= params.KICK_Y_MIN[RIGHT]:
        kick_parameter = (foot_y - params.KICK_Y_MAX[RIGHT])/(params.KICK_Y_MIN[RIGHT] - params.KICK_Y_MAX[RIGHT])
        print "RIGHT side, with parameter: ", kick_parameter
        return RIGHT, kick_parameter
    elif foot_y >= params.KICK_Y_MIN[LEFT]-margin and foot_y <= params.KICK_Y_MAX[LEFT]:
        print "MARGIN KICK: LEFT side, with parameter: 1.0"
        return LEFT, 1.0
    elif foot_y <= params.KICK_Y_MAX[LEFT]+margin and foot_y >= params.KICK_Y_MIN[LEFT]:
        print "MARGIN KICK: LEFT side, with parameter: 0.0"
        return LEFT, 0.0
    elif foot_y <= params.KICK_Y_MIN[RIGHT]+margin and foot_y >= params.KICK_Y_MAX[RIGHT]:
        print "MARGIN KICK: RIGHT side, with parameter: 1.0"
        return RIGHT, 1.0
    elif foot_y >= params.KICK_Y_MAX[RIGHT]-margin and foot_y <= params.KICK_Y_MIN[RIGHT]:
        print "MARGIN KICK: RIGHT side, with parameter: 0.0"
        return RIGHT, 0.0
    return None, None

def lookUpDelta(goal_bearing):
    for i in range(len(delta_table)):
        if goal_bearing == delta_table[i][0]:
            return delta_table[i][1]
        if goal_bearing < delta_table[i][0]:
            if i==0:
                return None
            return (delta_table[i-1][1] - 0.5*(delta_table[i][0]-goal_bearing)/(delta_table[i][0]-delta_table[i-1][0]))
    return None

def isInEllipse(ball_x, ball_y, foot, margin):
    #TODO: check if margin is legit
    radius = (params.KICK_Y_MAX[foot]-params.KICK_Y_MIN[foot])/2
    y_center = (params.KICK_Y_MAX[foot]+params.KICK_Y_MIN[foot])/2    
    a = radius + margin
    b = params.KICK_X_MAX[foot]-params.KICK_X_MIN[foot]
    if ((ball_y-y_center)**2)/(a**2)+((ball_x-params.KICK_X_MIN[foot])**2)/(b**2)<=1:
        print "IN ELLIPSE: ball close enough"        
        return True
    print "OUT OF ELLIPSE: ball too far"
    return False

