###############
# Game States #
###############
InitialGameState = 0; 
ReadyGameState = 1; 
SetGameState = 2; 
PlayGameState = 3; 
FinishGameState = 4;
# PenalizedGameState = 666; # TODO: Should I have something like this?

#########
# Teams #
#########
TeamA = 0; 
TeamB = 1;

#############
# Penalties #
#############
Standard = 0;
BallHoldingPenalty = 1;
GoaliePushingPenalty = 2;
PlayerPushingPenalty = 3;
IllegalDefenderPenalty = 4;
IllegalDefensePenalty = 5;
ObstructionPenalty = 6;
PickUpRequest = 7; # TODO: I'm not taking this into account at the moment.
LeavingField = 8; # TODO: I'm not taking this into account at the moment.
Damage = 9; # TODO: I'm not taking this into account at the moment.
Manual = 10 # TODO: Is this correct?

Penalties = [BallHoldingPenalty, GoaliePushingPenalty, PlayerPushingPenalty, IllegalDefenderPenalty, IllegalDefensePenalty, ObstructionPenalty]

UNKNOWN_GAME_STATE = object() # Ensures uniqueness, and won't test as equal to anything other than itself.
UNKNOWN_PLAYER_STATUS = object() # Ensures uniqueness, and won't test as equal to anything other than itself.
