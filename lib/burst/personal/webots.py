""" Personal file for webots """

## Behavior params
import burst.behavior_params as params
params.KICK_X_MIN = [17.5,17.5] #[30.0,30.0]
params.KICK_X_MAX = [21.0,21.0] #[33.0,33.0]
params.KICK_Y_MIN = [4.0,-4.0] #[6.0,-6.0]
params.KICK_Y_MAX = [10.0,-10.0] #[12.5,-12.5]
params.MOVEMENT_PERCENTAGE_FORWARD = 0.9 # was 0.55, lets try 0.9...
params.MOVEMENT_PERCENTAGE_SIDEWAYS = 0.9
params.MOVEMENT_PERCENTAGE_TURN = 0.9


import burst.actions.actionconsts as actionconsts
actionconsts.DEFAULT_STEPS_FOR_TURN = 60
