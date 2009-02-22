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
