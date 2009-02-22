"""
StopWalk

Small example to show use of taks ids.

"""

from motion_CurrentConfig import *



#####
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


try:
  ttsProxy = ALProxy("ALTextToSpeech")
except Exception,e:
  pass
  

# ============================================================

motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

motionProxy.setWalkArmsEnable(True)



#Walk
# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )

# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )


motionProxy.addWalkStraight( 10, 25 )

walkTaskId = motionProxy.post.walk() #non blocking call, we can do something else


previousHeadAngle = motionProxy.getAngle("HeadYaw");

motionProxy.setChainStiffness("Head",0.0,0.5)
  

time.sleep(2)
if ( ttsProxy ):
  ttsProxy.say("Move my head if you want me to stop")

while (motionProxy.isRunning(walkTaskId)):
  if( abs(motionProxy.getAngle("HeadYaw") - previousHeadAngle) > 0.1):
    motionProxy.clearFootsteps()
  time.sleep(1)

motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
