"""
Walk

Small example to make Nao walk

"""

from motion_CurrentConfig import *


####
# Create python broker

try:
  broker = ALBroker("pythonBroker","127.0.0.1",9999,IP, PORT)
except RuntimeError,e:
  print("cannot connect")
  exit(1)

####
# Create motion proxy

print "Creating motion proxy"


try:
  motionProxy = ALProxy("ALMotion")
except Exception,e:
  print "Error when creating motion proxy:"
  print str(e)
  exit(1)

# ============================================================

#SIDESTEP_WALK = Walk(WalkParameters([
#           100.0 * DEG_TO_RAD, # ShoulderMedian
#           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
#           20.0 * DEG_TO_RAD,  # ElbowMedian
#           10.0 * DEG_TO_RAD,  # ElbowAmplitude
#           4.5,                   # LHipRoll(degrees)
#           -4.5,                  # RHipRoll(degrees)
#           0.19,                  # HipHeight(meters)
#           5.0,                   # TorsoYOrientation(degrees)
#           0.02,                  # StepLength
#           0.015,                  # StepHeight
#           0.04,                  # StepSide
#           0.3,                   # MaxTurn
#           0.015,                  # ZmpOffsetX
#           0.02]),                  # ZmpOffsetY
#           25                   # 20ms count per step
#    )

#SLOW_WALK = Walk(WalkParameters([
#           100.0 * DEG_TO_RAD, # ShoulderMedian
#           15.0 * DEG_TO_RAD,  # ShoulderAmplitude
#           30.0 * DEG_TO_RAD,  # ElbowMedian
#           10.0 * DEG_TO_RAD,  # ElbowAmplitude
#           4.5,                   # LHipRoll(degrees)
#           -4.5,                  # RHipRoll(degrees)
#           0.22,                  # HipHeight(meters)
#           3.4,                   # TorsoYOrientation(degrees)
#           0.070,                  # StepLength
#           0.043,                  # StepHeight
#           0.03,                  # StepSide
#           0.3,                   # MaxTurn
#           0.01,                  # ZmpOffsetX
#           0.00]),                  # ZmpOffsetY
#           80          # 20ms count per step
#    )

#FASTER_WALK = WalkParameters([
#           110.0 * DEG_TO_RAD, # ShoulderMedian
#           10.0 * DEG_TO_RAD,  # ShoulderAmplitude
#           90.0 * DEG_TO_RAD,  # ElbowMedian
#           0.0 * DEG_TO_RAD,  # ElbowAmplitude
#           4.5,                   # LHipRoll(degrees) (2.5 original)
#           -4.5,                  # RHipRoll(degrees) (-2.5 original)
#           0.23,                  # HipHeight(meters)
#           0.0,                   # TorsoYOrientation(degrees)
#           0.04,                  # StepLength
#           0.02,                  # StepHeight
#           0.02,                  # StepSide
#           0.3,                   # MaxTurn
#           0.01,                  # ZmpOffsetX
#           0.016,                 # ZmpOffsetY
#           18])#,                    # 20ms count per step
#           #,0.68]                  # Angle 0.68

readyStand = [0.065920039999999999,
 -0.65199196000000004,
 1.7471840000000001,
 0.25460203999999997,
 -1.5662560000000001,
 -0.33130205000000001,
 -0.012313961999999999,
 0.0072991871,
 0.0061779618000000003,
 -0.0076280384999999999,
 -0.78536605999999998,
 1.5431621,
 -0.78238200999999996,
 0.016915962,
 0.0061779618000000003,
 0.072139964000000001,
 -0.77931397999999996,
 1.53711,
 -0.79303604000000005,
 -0.073590039999999995,
 1.734996,
 -0.25008397999999998,
 1.5646381,
 0.36053199000000002,
 0.019900039000000001,
 0.0014810241000000001]


motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
# ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 20.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
motionProxy.setWalkArmsEnable(True)

# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.24, 2.0 )
# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY
motionProxy.setWalkConfig( 0.035, 0.045, 0.04, 0.3, 0.015, 0.03 )
motionProxy.addWalkStraight( 0.07*8, 35)
motionProxy.gotoBodyAnglesWithSpeed(readyStand,20,1)
time.sleep(3)
motionProxy.walk()

exit(0)





motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)



# ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
motionProxy.setWalkArmsEnable(True)

#################
## Slow Walk With High Step
#################

# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.22, 2.0 )

# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY
motionProxy.setWalkConfig( 0.05, 0.04, 0.04, 0.4, 0.01, 0.00 )

motionProxy.addWalkStraight( 0.05*4, 80)
#motionProxy.addTurn( 0.4*4, 80 )
#motionProxy.addWalkSideways(-0.04*4, 80)
motionProxy.walk()   #Blocking Function

exit(0)

#################
## Speed Walk
#################

# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )

# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY
motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )

motionProxy.addWalkStraight( 0.04*4, 25)
motionProxy.addTurn( 0.3*5, 25 )
motionProxy.addWalkSideways(0.02*8, 25)
motionProxy.addWalkArc( 0.3*4, 0.3, 25 )
motionProxy.addWalkSideways(-0.02*8, 25)
motionProxy.addWalkStraight( -0.05*3, 25)

motionProxy.walk()   #Blocking Function
