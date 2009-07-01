""" Personal file for a robot by the name of this file. """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [14,14]
params.KICK_X_MAX = [20,20]
params.KICK_Y_MIN = [3.5,-4.5]
params.KICK_Y_MAX = [7,-8]

#import burst.moves.walks as walks
#walks.STRAIGHT_WALK.defaultSpeed = 100 # Eran: 80 seems to fall within ~40cm when running kicker, need to check 100 (150 works for sure)
#walks.SIDESTEP_WALK.defaultSpeed = 20 # 20 seems just fine
