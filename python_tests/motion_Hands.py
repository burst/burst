"""
Hands

Small example to make Nao open ad close his hands.


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

#Get the Number of Joints
NumJoints = len(motionProxy.getBodyJointNames())

if (NumJoints != 26):
  print "This Nao seems to have no hands..."
  exit(1)

##
# First example using openHand:

def movehand(whichhand="LHand"):
    motionProxy.setJointStiffness(whichhand,1.0,1)
    time.sleep(1)
    motionProxy.openHand(whichhand)
    motionProxy.closeHand(whichhand)
    # Stiffness is automatically removed after calling this method.

    ##
    # Second example using gotoAngle:
    motionProxy.setJointStiffness(whichhand,1.0,1)
    time.sleep(1)
    motionProxy.gotoAngle(whichhand,0.5,1,motion.INTERPOLATION_SMOOTH)
    motionProxy.gotoAngle(whichhand,0.0,1,motion.INTERPOLATION_SMOOTH)
    # Warning! You MUST set back stiffness to zero for hands. Motors are fragil:

    motionProxy.setJointStiffness(whichhand,0.0,1)

if __name__ == '__main__':
    movehand("RHand")
    movehand("LHand")
