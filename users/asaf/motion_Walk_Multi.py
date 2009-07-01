"""
Walk

Small example to make Nao walk

"""

from motion_CurrentConfig import *

import sys

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

if len(sys.argv) > 1:
  print "walking ",sys.argv[1]
  walk = int(sys.argv[1])
else:
  walk = FASTER

motionProxy.setBodyStiffness(0.9,0.5)
time.sleep(0.5)
motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

if walk == SLOW:

  #################
  ## Slow Walk With High Step
  #################

  param = [100.0 * motion.TO_RAD, # ShoulderMedian
           10.0 * motion.TO_RAD,  # ShoulderAmplitude
           30.0 * motion.TO_RAD,  # ElbowMedian
           10.0 * motion.TO_RAD,  # ElbowAmplitude
           4.5,                   # LHipRoll(degrees)
           -4.5,                  # RHipRoll(degrees)
           0.22,                  # HipHeight(meters)
           2.0,                   # TorsoYOrientation(degrees)
           0.05,                  # StepLength
           0.04,                  # StepHeight
           0.04,                  # StepSide
           0.4,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.00,                  # ZmpOffsetY
           0.05*4,                # Distance
           80]                    # Speed

elif walk == FAST:
  #################
  ## Speed Walk
  #################

  param = [100.0 * motion.TO_RAD, # ShoulderMedian
           10.0 * motion.TO_RAD,  # ShoulderAmplitude
           30.0 * motion.TO_RAD,  # ElbowMedian
           10.0 * motion.TO_RAD,  # ElbowAmplitude
           3.5,                   # LHipRoll(degrees)
           -3.5,                  # RHipRoll(degrees)
           0.23,                  # HipHeight(meters)
           3.0,                   # TorsoYOrientation(degrees)
           0.04,                  # StepLength
           0.02,                  # StepHeight
           0.02,                  # StepSide
           0.3,                   # MaxTurn
           0.015,                 # ZmpOffsetX
           0.018,                 # ZmpOffsetY
           0.8,                   # Distance
           25]                    # Speed

elif walk == STANDARD:
  #################
  ## Standard Walk
  #################

  param = [100.0 * motion.TO_RAD, # ShoulderMedian
           10.0 * motion.TO_RAD,  # ShoulderAmplitude
           30.0 * motion.TO_RAD,  # ElbowMedian
           10.0 * motion.TO_RAD,  # ElbowAmplitude
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
           0.5,                   # Distance
           25]                    # Speed

elif walk == HAPPY:
  #################
  ## Happy Walk
  #################

  param = [-100.0 * motion.TO_RAD,# ShoulderMedian
           10.0 * motion.TO_RAD,  # ShoulderAmplitude
           10.0 * motion.TO_RAD,  # ElbowMedian
           10.0 * motion.TO_RAD,  # ElbowAmplitude
           2.5,                   # LHipRoll(degrees)
           -2.5,                  # RHipRoll(degrees)
           0.22,                  # HipHeight(meters)
           0.0,                   # TorsoYOrientation(degrees)
           0.01,                  # StepLength
           0.02,                  # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.018,                 # ZmpOffsetY
           0.05,                  # Distance
           20]                    # Speed

elif walk == SKI:
  #################
  ## Cross Country Ski Walk
  #################

  param = [60.0 * motion.TO_RAD,  # ShoulderMedian
           60.0 * motion.TO_RAD,  # ShoulderAmplitude
           30.0 * motion.TO_RAD,  # ElbowMedian
           -30.0 * motion.TO_RAD, # ElbowAmplitude
           3.5,                   # LHipRoll(degrees)
           -3.5,                  # RHipRoll(degrees)
           0.21,                  # HipHeight(meters)
           0.0,                   # TorsoYOrientation(degrees)
           0.06,                  # StepLength
           0.001,                 # StepHeight
           0.03,                  # StepSide
           0.3,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.018,                 # ZmpOffsetY
           0.3,                   # Distance
           30]                    # Speed

elif walk == FASTER:
  #################
  ## Really fast Walk
  #################

  param = [110.0 * motion.TO_RAD, # ShoulderMedian
           10.0 * motion.TO_RAD,  # ShoulderAmplitude
           90.0 * motion.TO_RAD,  # ElbowMedian
           00.0 * motion.TO_RAD,  # ElbowAmplitude
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
           1,                     # Distance
           18,                    # Speed
           0.68]                  # Angle

elif walk == SLOWER:
  #################
  ## Really Slow Walk
  #################

  param = [100.0 * motion.TO_RAD, # ShoulderMedian
           10.0 * motion.TO_RAD,  # ShoulderAmplitude
           30.0 * motion.TO_RAD,  # ElbowMedian
           10.0 * motion.TO_RAD,  # ElbowAmplitude
           4.5,                   # LHipRoll(degrees) (2.5 original)
           -4.5,                  # RHipRoll(degrees) (-2.5 original)
           0.23,                  # HipHeight(meters)
           2.0,                   # TorsoYOrientation(degrees)
           0.05,                  # StepLength
           0.02,                  # StepHeight
           0.04,                  # StepSide
           0.4,                   # MaxTurn
           0.01,                  # ZmpOffsetX
           0.00,                  # ZmpOffsetY
           0.2,                   # Distance
           120]                   # Speed


else:
  exit(0)

# ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
motionProxy.setWalkArmsConfig( param[0], param[1], param[2], param[3] )
motionProxy.setWalkArmsEnable(True)

# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
motionProxy.setWalkExtraConfig( param[4], param[5], param[6], param[7] )

# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY
motionProxy.setWalkConfig( param[8], param[9], param[10], param[11], param[12], param[13] )

if len(param) == 16:
  motionProxy.addWalkStraight( param[14], param[15] )
elif len(param) == 17:
  motionProxy.addWalkArc( param[14], param[16], param[15] )
else:
  print "ERROR: wrong number of parameters"
  exit(0)
#motionProxy.addTurn( 0.3*5, 25 )
#motionProxy.addWalkSideways(0.02*8, 25)
#motionProxy.addWalkArc( 0.3*4, 0.3, 25 )
#motionProxy.addWalkSideways(-0.02*8, 25)
#motionProxy.addWalkStraight( -0.05*3, 25)
#motionProxy.addTurn( 0.4*4, 80 )
#motionProxy.addWalkSideways(-0.04*4, 80)
motionProxy.walk()   #Blocking Function


