""" Personal file for a robot by the name of this file. """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [12,12]
params.KICK_X_MAX = [18,18]
params.KICK_Y_MIN = [3.5,-1.5]
params.KICK_Y_MAX = [9.5,-8.5]

#import burst.moves.walks as walks
#walks.STRAIGHT_WALK.defaultSpeed = 100 # Eran: 80 seems to fall within ~40cm when running kicker, need to check 100 (150 works for sure)
#walks.SIDESTEP_WALK.defaultSpeed = 20 # 20 seems just fine
