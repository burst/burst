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
#new walk
motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 20.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
#old walk
#motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 15.0 * motion.TO_RAD )
motionProxy.setWalkArmsEnable(True)

# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
# Cech asymetric
#motionProxy.setWalkExtraConfig( 4.5, -2.5, 0.19, 5.0 )
motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.19, 2.0 )
# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY

# Cech
#motionProxy.setWalkConfig( 0.02, 0.015, 0.04, 0.3, 0.015, 0.02 )
#motionProxy.addWalkStraight( 0.02*2, 23)
# Speed = 20
#motionProxy.setWalkConfig( 0.015, 0.015, 0.04, 0.3, 0.015, 0.025)
#motionProxy.addWalkStraight( 0.5, 20)
# Speed = 21 step = 0.2
motionProxy.setWalkConfig( 0.025, 0.015, 0.04, 0.3, 0.015, 0.02) #WORKS!
motionProxy.addWalkStraight( 0.4, 21) #WORKS!
# Speed = 21 step = 0.15
#motionProxy.setWalkConfig( 0.015, 0.015, 0.04, 0.3, 0.015, 0.02) #WORKS!
#motionProxy.addWalkStraight( 0.4, 21) #WORKS!
# Speed = 25
#motionProxy.setWalkConfig( 0.015, 0.015, 0.04, 0.3, 0.015, 0.02 ) #WORKS!
#motionProxy.addWalkStraight( 0.4, 25) #WORKS!
motionProxy.gotoBodyAnglesWithSpeed(readyStand,20,1)
time.sleep(3)


#motionProxy.addWalkStraight( 0.02*16, 20)
#motionProxy.addWalkStraight( 0.02*2, 23)
#motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.19, 5.0 )
#motionProxy.addWalkStraight( 0.025*4, 122)
motionProxy.walk()

exit(0)

