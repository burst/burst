import burst_consts
import burst_events

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
TeamA = BlueTeam = 0;
TeamB = RedTeam = 1;

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

# Ensures uniqueness, and won't test as equal to anything other than itself.
class UNKNOWN_GAME_STATE(object):
    pass

# Ensures uniqueness, and won't test as equal to anything other than itself.
class UNKNOWN_PLAYER_STATUS(object):
    pass

#####################
# Robot Game States #
#####################
InitialRobotState = 0;
ReadyRobotState = 1;
SetRobotState = 2;
PlayRobotState = 3;
PenalizedRobotState = 4;

GameStateToRobotStateMap = dict([(i, i) for i in xrange(5)])
GameStateToRobotStateMap[UNKNOWN_GAME_STATE] = UNKNOWN_PLAYER_STATUS

robotStateToChestButtonColor = {
    InitialRobotState : burst_consts.OFF,
    ReadyRobotState : burst_consts.BLUE,
    SetRobotState : burst_consts.YELLOW,
    PlayRobotState : burst_consts.GREEN,
    PenalizedRobotState : burst_consts.RED,
    UNKNOWN_PLAYER_STATUS : burst_consts.RED}

state_names = ['Initial', 'Ready', 'Set', 'Play', 'Finish']
gamestates = [globals()[x+'GameState'] for x in state_names]
gamestate_to_to_event = dict([(gamestate, getattr(burst_events, 'EVENT_SWITCHED_TO_' + state.upper() + '_GAME_STATE'))
        for state, gamestate in zip(state_names, gamestates)])
gamestate_to_from_event = dict([(gamestate, getattr(burst_events, 'EVENT_SWITCHED_FROM_' + state.upper() + '_GAME_STATE'))
        for state, gamestate in zip(state_names, gamestates)])

# Debugging helpers
game_state_to_string_d = {
    InitialGameState: 'Initial',
    SetGameState: 'Set',
    ReadyGameState: 'Ready',
    PlayGameState: 'Play',
    FinishGameState: 'Finish',
    UNKNOWN_GAME_STATE: 'UNKNOWN'
}

def gameStateToString(state):
    return game_state_to_string_d[state]

