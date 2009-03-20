""" Test our brand new Locomotion class
"""

from walkAPI import Locomotion

c = Locomotion("127.0.0.1",9111)
c.memoryProxy.insertData("Burst/Odometry/X",0.5,0)
c.memoryProxy.insertData("Burst/Odometry/Y",0,0)
c.memoryProxy.insertData("Burst/Odometry/Yaw",-1.57009,0)

#c.testWalk()
c.goToLocation(1,0,0)
print "aaaa"
