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
SLOW = 0
FAST = 1
STANDARD = 2
HAPPY = 3
SKI = 4
FASTER = 5
SLOWER = 6

walk = FASTER

motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

if walk == SLOW:

  #################
  ## Slow Walk With High Step
  #################

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.22, 2.0 )

  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.05, 0.04, 0.04, 0.4, 0.01, 0.00 )

  motionProxy.addWalkStraight( 0.05*4, 80)
  #motionProxy.addTurn( 0.4*4, 80 )
  #motionProxy.addWalkSideways(-0.04*4, 80)
  motionProxy.walk()   #Blocking Function

  #exit(0)
elif walk == FAST:
  #################
  ## Speed Walk
  #################

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )
  #motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.23, 3.0 ) #Vova Suggested
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )

  motionProxy.addWalkStraight( 0.8, 25)
  #motionProxy.addTurn( 0.3*5, 25 )
  #motionProxy.addWalkSideways(0.02*8, 25)
  #motionProxy.addWalkArc( 0.3*4, 0.3, 25 )
  #motionProxy.addWalkSideways(-0.02*8, 25)
  #motionProxy.addWalkStraight( -0.05*3, 25)
  motionProxy.walk()   #Blocking Function
elif walk == STANDARD:
  #################
  ## Standard Walk
  #################

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 2.5, -2.5, 0.23, 0.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.04, 0.02, 0.03, 0.3, 0.01, 0.018)

  motionProxy.addWalkStraight( 0.5, 25)
  motionProxy.walk()

elif walk == HAPPY:
  #################
  ## Happy Walk
  #################

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( -100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 2.5, -2.5, 0.22, 0.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.01, 0.02, 0.03, 0.3, 0.01, 0.018)

  motionProxy.addWalkStraight( 0.01*5, 20)
  motionProxy.walk()

elif walk == SKI:
  #################
  ## Cross Country Ski Walk
  #################

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( 60.0 * motion.TO_RAD, 60.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, -30.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.21, 0.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.06, 0.001, 0.03, 0.3, 0.01, 0.018)

  motionProxy.addWalkStraight( 0.06*5, 30)
  motionProxy.walk()

elif walk == FASTER:
  #################
  ## Really fast Walk
  #################

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( 110.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 90.0 * motion.TO_RAD, 0.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)
  
  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  #motionProxy.setWalkExtraConfig( 2.5, -2.5, 0.23, 0.0 ) #Original
  motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.23, 0.0 ) #Vova suggested
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  #motionProxy.setWalkConfig( 0.04, 0.02, 0.03, 0.3, 0.01, 0.016) #Original
  motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.01, 0.016)

  #motionProxy.addWalkStraight( 0.4, 18)
  motionProxy.addWalkArc( 3, 0.67, 18 )
  motionProxy.walk()

elif walk == SLOWER:
  #################
  ## Really Slow Walk
  #################

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.23, 2.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.05, 0.02, 0.04, 0.4, 0.01, 0.00 )

  motionProxy.addWalkStraight( 0.05*4, 120)
  motionProxy.walk()

