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

## General moves
#import burst.moves.general_moves as general_moves
#general_moves.SIT_POS[:] = [
#           ((0.,90.,0.,0.),
#            (-12.5, -5., -42.5, 125., -70., 6.),
#            (-12.5, 5., -42.5, 125., -70., -6.),
#            (0.,-90.,0.,0.),3.0),
#           ((55.,7.,0.,-30.),
#            (-12.5, -5., -42.5, 125., -70., 6.),
#            (-12.5, 5., -42.5, 125., -70., -6.),
#            (55.,-7.,0.,30.),1.5)]

## Walks

import burst.moves.walks as walks
walks.STRAIGHT_WALK.defaultSpeed = 100

## Behavior params

import burst.behavior_params as params
params.KICK_X_MIN[:] = [14.0, 14.0]
params.KICK_X_MAX[:] = [20.0, 20.0]
params.KICK_Y_MIN[:] = [2.0, -3.5]
params.KICK_Y_MAX[:] = [5.0, -6.5]
