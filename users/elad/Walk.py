"""
Walk
"""

import burst
burst.init()
motionProxy = burst.getMotionProxy()
motion = burst.motion

class WalkType:
	SLOW = 0
	FAST = 1
	STANDARD = 2
	HAPPY = 3
	SKI = 4
	FASTER = 5
	SLOWER = 6


def walk(walk_type, distance):
	if walk_type == WalkType.SLOW: 
		slow_walk(distance)
	elif walk_type == WalkType.FAST: 
		fast_walk(distance)
	elif walk_type == WalkType.STANDARD: 
		standard_walk(distance)
	elif walk_type == WalkType.HAPPY: 
		happy_walk(distance)
	elif walk_type == WalkType.SKI: 
		ski_walk(distance)
	elif walk_type == WalkType.FASTER: 
		faster_walk(distance)
	elif walk_type == WalkType.SLOWER: 
		slower_walk(distance)
	

motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)


  #################
  ## Slow Walk With High Step
  #################
def slow_walk(distance):

  motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
  
  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.22, 2.0 )

  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.05, 0.04, 0.04, 0.4, 0.01, 0.00 )

  motionProxy.addWalkStraight(distance, 80)
  #motionProxy.addTurn( 0.4*4, 80 )
  #motionProxy.addWalkSideways(-0.04*4, 80)
  motionProxy.walk()   #Blocking Function


  #################
  ## Speed Walk
  #################
def fast_walk(distance):

  motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude 
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )
  #motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.23, 3.0 ) #Vova Suggested
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )

  motionProxy.addWalkStraight(distance, 25)
  #motionProxy.addTurn( 0.3*5, 25 )
  #motionProxy.addWalkSideways(0.02*8, 25)
  #motionProxy.addWalkArc( 0.3*4, 0.3, 25 )
  #motionProxy.addWalkSideways(-0.02*8, 25)
  #motionProxy.addWalkStraight( -0.05*3, 25)
  motionProxy.walk()   #Blocking Function


  #################
  ## Standard Walk
  #################
def standard_walk(distance):

  motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 2.5, -2.5, 0.23, 0.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.04, 0.02, 0.03, 0.3, 0.01, 0.018)

  motionProxy.addWalkStraight(distance, 25)
  motionProxy.walk()


  #################
  ## Happy Walk
  #################
def happy_walk(distance):

  motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( -100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 2.5, -2.5, 0.22, 0.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.01, 0.02, 0.03, 0.3, 0.01, 0.018)

  motionProxy.addWalkStraight(distance, 20)
  motionProxy.walk()


  #################
  ## Cross Country Ski Walk
  #################
def ski_walk(distance):

  motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( 60.0 * motion.TO_RAD, 60.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, -30.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.21, 0.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.06, 0.001, 0.03, 0.3, 0.01, 0.018)

  motionProxy.addWalkStraight(distance, 30)
  motionProxy.walk()


  #################
  ## Really fast Walk
  #################
def faster_walk(distance):

  motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

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
  motionProxy.addWalkArc(distance, 0.67, 18 ) # TODO
  motionProxy.walk()


  #################
  ## Really Slow Walk
  #################
def slower_walk(distance):

  motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

  # ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude
  motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
  motionProxy.setWalkArmsEnable(True)

  # LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
  motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.23, 2.0 )
  # StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
  motionProxy.setWalkConfig( 0.05, 0.02, 0.04, 0.4, 0.01, 0.00 )

  motionProxy.addWalkStraight(distance, 120)
  motionProxy.walk()

