from burst.consts import DEG_TO_RAD
from burst.world import World
from .. import walkparameters; WalkParameters = walkparameters.WalkParameters


class Walk(list):

    SlowestSpeed, FastestSpeed, DefaultSpeed = object(), object(), object()

    def __init__(self, walkParameters, defaultSpeed=None, slowestSpeed=150, fastestSpeed=100):
        self.walkParameters = walkParameters
        self.slowestSpeed = slowestSpeed
        self.fastestSpeed = fastestSpeed
        if defaultSpeed is None:
            self.defaultSpeed = slowestSpeed
        else:
            self.defaultSpeed = defaultSpeed

    def fractionalSpeed(self, fraction):
        return self.slowestSpeed - (self.slowestSpeed-self.fastestSpeed)*fraction

    def __getitem__(self, key):
        if key == Walk.SlowestSpeed: return self.slowestSpeed
        elif key == Walk.FastestSpeed: return self.fastestSpeed
        elif key == Walk.DefaultSpeed: return self.defaultSpeed
        else: return self.walkParameters[key]

    def __setitem__(self, key, value):
        if key == Walk.SlowestSpeed: self.slowestSpeed = value
        elif key == Walk.FastestSpeed: self.fastestSpeed = value
        elif key == Walk.DefaultSpeed: self.defaultSpeed = value
        else: self.walkParameters[key] = value




# WALKS
FASTEST_WALK_WEBOTS = Walk([
           100.0 * DEG_TO_RAD, # 0 ShoulderMedian
           10.0 * DEG_TO_RAD,    # 1 ShoulderAmplitude
           30.0 * DEG_TO_RAD,    # 2 ElbowMedian 
           10.0 * DEG_TO_RAD,    # 3 ElbowAmplitude 
           2.5,                  # 4 LHipRoll(degrees) 
           -2.5,                 # 5 RHipRoll(degrees)
           0.23,                 # 6 HipHeight(meters)
           3.0,                  # 7 TorsoYOrientation(degrees)
           0.07,                 # 8 StepLength
           0.042,                 # 9 StepHeight
           0.06,                 # 10 StepSide (was 0.02)
           0.3,                  # 11 MaxTurn
           0.015,                # 12 ZmpOffsetX
           0.018],                # 13 ZmpOffsetY 
           54)                  # 14 20ms count per step

SLOW_WALK = Walk([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           15.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           10.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) 
           -4.5,                  # RHipRoll(degrees)
           0.22,                  # HipHeight(meters)
           3.4,                   # TorsoYOrientation(degrees)
           0.070,                  # StepLength
           0.043,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.00],                  # 
           80          # 20ms count per step
    )

if World.connected_to_nao:
    FASTEST_WALK = SLOW_WALK
else:
    FASTEST_WALK = FASTEST_WALK_WEBOTS






'''
    UNUSED WALKS!!!
    stored here for possible future use of parameters
'''



'''
FAST_WALK_WEBOTS = WalkParameters([
           110.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           90.0 * DEG_TO_RAD,  # ElbowMedian 
           0.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) (2.5 original)
           -4.5,                  # RHipRoll(degrees) (-2.5 original)
           0.23,                  # HipHeight(meters) MAX
           0.0,                   # TorsoYOrientation(degrees)
           0.04,                  # StepLength MAX
           0.025,                  # StepHeight MAX
           0.02,                  # StepSide
           0.3,                   # MaxTurn
           0.06,                  # ZmpOffsetX MAX
           0.016,                 # ZmpOffsetY 
           18])

FASTER_WALK = WalkParameters([
           110.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           90.0 * DEG_TO_RAD,  # ElbowMedian 
           0.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4.5,                   # LHipRoll(degrees) (2.5 original)
           -4.5,                  # RHipRoll(degrees) (-2.5 original)
           0.23,                  # HipHeight(meters)
           0.0,                   # TorsoYOrientation(degrees)
           0.04,                  # StepLength
           0.02,                  # StepHeight
           0.02,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.016,                 # ZmpOffsetY 
           18])#,                    # 20ms count per step
           #,0.68]                  # Angle 0.68

FAST_WALK = WalkParameters([
           100.0 * DEG_TO_RAD, # 0 ShoulderMedian
           10.0 * DEG_TO_RAD,    # 1 ShoulderAmplitude
           30.0 * DEG_TO_RAD,    # 2 ElbowMedian 
           10.0 * DEG_TO_RAD,    # 3 ElbowAmplitude 
           3.5,                  # 4 LHipRoll(degrees) 
           -3.5,                 # 5 RHipRoll(degrees)
           0.23,                 # 6 HipHeight(meters)
           3.0,                  # 7 TorsoYOrientation(degrees)
           0.04,                 # 8 StepLength
           0.02,                 # 9 StepHeight
           0.02,                 # 10 StepSide
           0.3,                  # 11 MaxTurn
           0.015,                # 12 ZmpOffsetX
           0.018,                # 13 ZmpOffsetY 
           # Not walk parameters proper.
           25])                   # 15 20ms count per step

STD_WALK = WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           10.0 * DEG_TO_RAD,  # ElbowAmplitude 
           2.5,                   # LHipRoll(degrees) 
           -2.5,                  # RHipRoll(degrees)
           0.23,                  # HipHeight(meters)
           0.0,                   # TorsoYOrientation(degrees)
           0.04,                  # StepLength
           0.02,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.018,                 # ZmpOffsetY 
           25])                    # 20ms count per step

SLOW_WALK1 = WalkParameters([
           100.0 * DEG_TO_RAD, # ShoulderMedian
           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
           30.0 * DEG_TO_RAD,  # ElbowMedian 
           10.0 * DEG_TO_RAD,  # ElbowAmplitude 
           4,                   # LHipRoll(degrees) 
           -4.5,                  # RHipRoll(degrees)
           0.19,                  # HipHeight(meters)
           5.0,                   # TorsoYOrientation(degrees)
           0.055,                  # StepLength
           0.042,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.015,                  # ZmpOffsetX
           0.00,                  # ZmpOffsetY 
           100])                    # 20ms count per step
'''

# TODO:
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Let the relevant robot personalization script runs its course, and change whatever it needs in this module. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

