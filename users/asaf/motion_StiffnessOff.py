"""
StiffnessOff

Contains some examples to set stiffness off for the whole body
of Nao, or chain by chain, or joint by joint

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

TimeInterpolation = 0.05

#**************************
# BODY
#**************************
  
print "Setting body stiffness to 0.0"
motionProxy.setBodyStiffness(0.0,TimeInterpolation)

#**************************
# CHAIN 
#**************************

# HEAD
#motionProxy.setChainStiffness('Head',0.0,TimeInterpolation);

# ARMS
#motionProxy.setChainStiffness('LArm',0.0,TimeInterpolation);
#motionProxy.setChainStiffness('RArm',0.0,TimeInterpolation);

# LEGS
#motionProxy.setChainStiffness('LLeg',0.0,TimeInterpolation);
#motionProxy.setChainStiffness('RLeg',0.0,TimeInterpolation);

#**************************
# JOINT 
#**************************

# HEAD
#motionProxy.setJointStiffness('HeadPitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('HeadYaw',0.0,TimeInterpolation)

# ARMS
#motionProxy.setJointStiffness('LShoulderPitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LShoulderRoll',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LElbowYaw',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LElbowRoll',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RShoulderPitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RShoulderRoll',0.0,TimeInterpolation0)
#motionProxy.setJointStiffness('RElbowYaw',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RElbowRoll',0.0,TimeInterpolation)

# LEGS
#motionProxy.setJointStiffness('LHipYawPitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LHipRoll',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LHipPitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LKneePitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LAnklePitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('LAnkleRoll',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RHipYawPitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RHipRoll',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RHipPitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RKneePitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RAnklePitch',0.0,TimeInterpolation)
#motionProxy.setJointStiffness('RAnkleRoll',0.0,TimeInterpolation)

time.sleep(TimeInterpolation)

print "Stiffness set to 0.0"
