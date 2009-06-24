import player_init # remove before inserting into code
import burst.behavior_params as params
from burst_consts import (LEFT, RIGHT)    
""" returns the correct foot and kicking type (if any) for a given goal angle and ball position relative to body.
    If a kick is not possible, it returns none as the kicking foot.
"""
delta_table = [(-0.55,4),(-0.44,3.5),(-0.38,3),(-0.31,2.5),(-0.24,2),(-0.14,1.5),(-0.09,1),(-0.03,0.5),(0,0),(0.07,-0.5),(0.1,-1),(0.12,-1.5),(0.19,-2),(0.24,-2.5),(0.33,-3),(0.42,-3.5),(0.52,-4)]

def getKickingType(goal_bearing, ball_y):
    # checks left foot then right foot - can't be both
    delta_y = lookUpDelta(goal_bearing)
    if delta_y == None:
        return None, None
    foot_y = delta_y + ball_y
    print "ball is at ", ball_y, ", delta is ", delta_y, ", so foot needs to be at ", foot_y
    print "Left foot range is [", params.KICK_Y_MIN[0], ",", params.KICK_Y_MAX[0], "]"
    print "Right foot range is [", params.KICK_Y_MAX[1], ",", params.KICK_Y_MIN[1], "]"
    if foot_y >= params.KICK_Y_MIN[0] and foot_y <= params.KICK_Y_MAX[0]:
        kick_parameter = 1 - (foot_y - params.KICK_Y_MIN[0])/(params.KICK_Y_MAX[0] - params.KICK_Y_MIN[0])
        print "LEFT side, with parameter: ", kick_parameter         
        return LEFT, kick_parameter
    if foot_y >= params.KICK_Y_MAX[1] and foot_y <= params.KICK_Y_MIN[1]:
        kick_parameter = (foot_y - params.KICK_Y_MAX[1])/(params.KICK_Y_MIN[1] - params.KICK_Y_MAX[1])
        print "RIGHT side, with parameter: ", kick_parameter
        return RIGHT, kick_parameter
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
