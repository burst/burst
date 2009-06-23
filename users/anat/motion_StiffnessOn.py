"""
StiffnessOn

Contains some examples to set stiffness off for the whole body
of Nao, or chain by chain, or joint by joint

You may wish to call this script first
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

print "Setting body stiffness to 1"
motionProxy.setBodyStiffness(1.0)

#**************************
# CHAIN
#**************************
# HEAD
#motionProxy.setChainStiffness('Head',1.0,TimeInterpolation);
# ARMS
#motionProxy.setChainStiffness('LArm',1.0,TimeInterpolation);
#motionProxy.setChainStiffness('RArm',1.0,TimeInterpolation);
# LEGS
#motionProxy.setChainStiffness('LLeg',1.0,TimeInterpolation);
#motionProxy.setChainStiffness('RLeg',1.0,TimeInterpolation);

#**************************
# JOINT
#**************************

# HEAD
#motionProxy.setJointStiffness('HeadPitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('HeadYaw',1.0,TimeInterpolation)

# ARMS
#motionProxy.setJointStiffness('LShoulderPitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LShoulderRoll',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LElbowYaw',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LElbowRoll',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RShoulderPitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RShoulderRoll',1.0,TimeInterpolation0)
#motionProxy.setJointStiffness('RElbowYaw',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RElbowRoll',1.0,TimeInterpolation)

# LEGS
#motionProxy.setJointStiffness('LHipYawPitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LHipRoll',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LHipPitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LKneePitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LAnklePitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('LAnkleRoll',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RHipYawPitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RHipRoll',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RHipPitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RKneePitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RAnklePitch',1.0,TimeInterpolation)
#motionProxy.setJointStiffness('RAnkleRoll',1.0,TimeInterpolation)

time.sleep(TimeInterpolation)

print "Stiffness set to 1.0"
