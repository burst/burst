"""
ComCommand

Small example to show how tu use the Com Command

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

kneeAngle = 60.0 * motion.TO_RAD

#Get the Number of Joints
NumJoints = len(motionProxy.getBodyJointNames())

# Define The Initial Position
if (NumJoints == 22) :
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, -80.0 * motion.TO_RAD,
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2, 0.0 * motion.TO_RAD,
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2,0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 80.0 * motion.TO_RAD]
elif (NumJoints == 26) :
  InitialPosition = [0.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, 15.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, -80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD,0.0,
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2, 0.0 * motion.TO_RAD,
    0.0, 0.0 * motion.TO_RAD, -kneeAngle/2, kneeAngle, -kneeAngle/2, -0.0 * motion.TO_RAD,
    120.0 * motion.TO_RAD, -15.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 80.0 * motion.TO_RAD, 0.0 * motion.TO_RAD, 0.0]
else :
  print "Unexpected number of Joint"
  exit(1)


motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)
# Send angles trough a smooth interpolation of one second.
motionProxy.gotoBodyAngles(InitialPosition , 1.0, motion.INTERPOLATION_SMOOTH)


# Go to Double Support Mode
motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)
time.sleep(1)
# Set the Balancer in COM Control Mode
motionProxy.setBalanceMode(motion.BALANCE_MODE_COM_CONTROL)


# Get The Initial Position of The COM in The Support Leg Space
InitialCom = motionProxy.getCom(motion.SPACE_SUPPORT_LEG)

# Print the Initial COM Position
print InitialCom

#Get the Initial Position of the Slave Leg i.e. Right Leg
InitialSlaveLegposition = motionProxy.getPosition('RLeg', motion.SPACE_SUPPORT_LEG)

# Move the COM with Smooth Interpolation in 3s
timeInterpolation = 3.0
Dx = +0.02
Dy = +0.02
Dz = -0.02
motionProxy.post.gotoCom(InitialCom[0]+Dx,InitialCom[1]+Dy,InitialCom[2]+Dz, timeInterpolation, motion.INTERPOLATION_SMOOTH)
motionProxy.gotoPosition('RLeg', motion.SPACE_SUPPORT_LEG, InitialSlaveLegposition, motion.AXIS_MASK_ALL, timeInterpolation, motion.INTERPOLATION_SMOOTH)

# Get The Final Position of The COM in The Support Leg Space
FinalCom = motionProxy.getCom(motion.SPACE_SUPPORT_LEG)

motionProxy.setBalanceMode(motion.BALANCE_MODE_OFF)

# Print Differences between Initial and Final COM Position
print "diff X = %.4f" % (FinalCom[0] - InitialCom[0])
print "diff Y = %.4f" % (FinalCom[1] - InitialCom[1])
print "diff Z = %.4f" % (FinalCom[2] - InitialCom[2])
