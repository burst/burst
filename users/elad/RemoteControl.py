import sys
import readline
import Robot
import Util
from Util import *

# TODO: If running on the robot, user 127.0.0.1 as the address?

Robot.init()
print "Controlling the robot at " + Robot.ip + ":" + str(Robot.port)

import BasicMotion

# Let the user choose an action, perform that action, repeat.
import Commands
from Commands import *

#motionProxy = Robot.getMotionProxy()
#print motionProxy.post.closeHand("RHand")
#motionProxy.post.closeHand("LHand")

#from Commands import CommandParser
#CompoundCommand([CommandParser.parseSingleCommand("openhand right"), CommandParser.parseSingleCommand("openhand left")], False).execute()
#CompoundCommand( [CompoundCommand([CommandParser.parseSingleCommand("closehand right"), CommandParser.parseSingleCommand("closehand left")], True)], True ).execute()

try:
	while True:
		selection = raw_input("> ")
		try:
			#x = Commands.CommandParser.parseSingleCommand(selection)
			x = Commands.CommandParser.parse(selection)
			x.execute()
			#print x.toString()
		except UnsupportedCommand:
			print "Error: Unsupported command."
		except ParseError:
			print "Error: Could not parse the command."
except TerminateSignal:
	pass

Robot.shutdown()
