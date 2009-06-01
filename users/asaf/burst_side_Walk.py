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

motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
# ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 20.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
motionProxy.setWalkArmsEnable(True)

# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.19, 5.0 )
# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
motionProxy.setWalkConfig( 0.025, 0.015, 0.03, 0.3, 0.015, 0.02 )
motionProxy.addWalkSideways(0.03*4, 18)
motionProxy.walk()

exit(0)

