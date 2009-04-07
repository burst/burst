"""
StopWalk

Small example to show use of taks ids.

"""

from motion_CurrentConfig import *

log = []
start_time = time.time()
def mylogger(something):
    
    class wrap(object):
        
        def __init__(self, obj):
            self.obj = obj
            if hasattr(obj, '__class__'):
                self.name = obj.__class__.__name__
            else:
                self.name = repr(obj)
            
        def __call__(self, *args, **kw):
            self.__log('__call__', args, kw)
            return self.obj(*args, **kw)
            
        def __getitem__(self, k):
            self.__log('__getitem__', [k])
            return self.obj.__getitem__(k)
            
        def __getattr__(self, k):
            self.__log('__getattr__', [k])
            return getattr(self.obj, k)
            
        def __log(self, what, args=[], kw={}):
            log.append((time.time() - start_time, '%s: %s: %r, %r' % (what, self.name, args, kw)))
            print '%3.2f: %s' % (log[-1][0], str(log[-1][1])[:80])
            
    return wrap(something)

ALProxy_real = ALProxy
def ALProxy(*args, **kw): return mylogger(ALProxy_real(*args, **kw))
    return ALProxy_real(*args, **kw)

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
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# create proxy
try:
  alultrasoundProxy = ALProxy("ALUltraSound",IP,PORT)
except RuntimeError,e:
  print "error while creation alultrasound's proxy"
  exit(1)

# subscribe to ALUltraound
try:
  period = 250 # minimum should be 240ms according to documentation
  alultrasoundProxy.subscribe("test", [ period ] )
  print "subscription to ALUltrasound is ok"
except RuntimeError,e:
  print "error while subscribing to alultrasound"
  exit(1)


# processing
# ....
print "processing"

# ====================
# Create proxy to ALMemory
memoryProxy = ALProxy("ALMemory",IP,PORT)


# ============================================================

motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

motionProxy.setWalkArmsEnable(True)



#Walk
# LHipRoll(degrees), RHipRoll(degrees), HipHeight(meters), TorsoYOrientation(degrees)
motionProxy.setWalkExtraConfig( 3.5, -3.5, 0.23, 3.0 )

# StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY 
motionProxy.setWalkConfig( 0.04, 0.02, 0.02, 0.3, 0.015, 0.018 )


motionProxy.addWalkStraight( 10, 25 )#add stuff to do. Once motionProxy.post.walk() is called the robot does all the stuff we added

walkTaskId = motionProxy.post.walk() #non blocking call, we can do something else. Once called the control returns imidiately to the user, instead of finishing the suff to do first and then retun to user.


previousHeadAngle = motionProxy.getAngle("HeadYaw");

motionProxy.setChainStiffness("Head",0.0)
  

#time.sleep(2)
#if ( ttsProxy ):
 # ttsProxy.say("Move my head if you want me to stop")

while (motionProxy.isRunning(walkTaskId)):
    US = memoryProxy.getData("extractors/alultrasound/distances", 0)
    print US
    if ((US[0] < 0.41) or (US[1] < 0.41)):
        print "going for a walk"
        motionProxy.clearFootsteps()#stops the walking
        motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)#stay steady
        motionProxy.addTurn( 0.3*5, 25 )#turn 90 deg left(?)
        motionProxy.walk()#stops the loop till finish turning
        motionProxy.addWalkStraight( 10, 25 )
        walkTaskId = motionProxy.post.walk() 
    if (abs(motionProxy.getAngle("HeadYaw") - previousHeadAngle) > 0.1):
        motionProxy.clearFootsteps()#stops the walking

print "bye bye"

  #time.sleep(0.025)

motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)#stay steady
