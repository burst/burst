""" Personal file for a robot by the name of this file.

PLEASE PAY ATTENTION TO THE FOLLOWING:

There is the good way to update stuff, and the bad way (asaf, I'm looking at you).

# BAD
import moves.walks as walks
walks.SIT_POS = [2,3,4]

# GOOD
import moves.walks as walks
walks.SIT_POS[:] = [2,3,4]

# ALSO GOOD
walks.SIT_POS[2] = 10

"""
import burst.moves.walks as walks
walks.STRAIGHT_WALK.defaultSpeed = 80

walks.SIT_POS = (((0.,91.,0.,0.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (0.,-90.,0.,0.),3.0),
           ((90.,0.,-65.,-57.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (0.,0.,-55.,125.7,-75.7,0.),
            (90.,0.,65.,57.),1.5))

import burst.behavior_params as params
params.KICK_X_MIN[:] = [14,14]
params.KICK_X_MAX[:] = [18,18]
params.KICK_Y_MIN[:] = [4.0,-2.5]
params.KICK_Y_MAX[:] = [6.0,-4.5]
