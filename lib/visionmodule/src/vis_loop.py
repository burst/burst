for i in range(0, 5):
  #time.sleep(0.5)
  print(i)

  #visionProxy.getBallRemote()
  visionProxy.getBall()

  val = memoryProxy.getData(memValue, 0)
  #val = 320

  # head between -2 (right) to 2 (left)
  # ball between 0 (left) to 640 (right)

  if(val):
    if(val>0):
      print "Ball X: ", val
      currentHeadYaw = motionProxy.getAngle("HeadYaw")
      print "currentHeadYaw: %f" % currentHeadYaw
      xtodeg = ((320.0-val)/320.0) # between 1 (left) to -1 (right)
      print "xtodeg: %f" % xtodeg
      
      if (abs(xtodeg)>0.05):
       xtodegfactor = 0.2
       newHeadYaw = currentHeadYaw + xtodeg*xtodegfactor
       print "newHeadYaw: %f" % newHeadYaw
       #motionProxy.setAngle("HeadYaw",(320.0-val)/320.0/2)
       motionProxy.gotoAngle("HeadYaw",newHeadYaw,TimeInterpolation*10,1)
       #print "test: %f" % ((320.0-val)/320.0/2)
  else:
    print "* No ball detected"

