# File:
# Date:
# Description:
# Author:
# Modifications:

# You may need to import some classes of the controller module. Ex:
#  from controller import CustomRobot, LED, DistanceSensor
#
# or to import the entire module. Ex:
#  from controller import *
from controller import Robot

# Here is the main class of your controller.
# This class defines how to initialize and how to run your controller.
# Note that this class derives Robot and so inherits all its functions
class MyController (Robot):

  # User defined function for initializing and running
  # the MyController class
  def run(self):

    # You should insert a getDevice-like function in order to get the
    # instance of a device of the robot. Something like:
    #  led = self.getLed('ledname')

    # Main loop
    while True:

      # Read the sensors:
      # Enter here functions to read sensor data, like:
      #  val = ds.getValue()

      # Process sensor data here.

      # Enter here functions to send actuator commands, like:
      #  led.set(1)

      # Perform a simulation step of 64 milliseconds
      # and leave the loop when the simulation is over
      if self.step(64) == -1: break

    # Enter here exit cleanup code

# The main program starts from here

# This is the main program of your controller.
# It creates an instance of your Robot subclass, launches its
# function(s) and destroys it at the end of the execution.
# Note that only one instance of Robot should be created in
# a controller program.
controller = MyController()
controller.run()
