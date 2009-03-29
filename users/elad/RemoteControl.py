import sys
import readline
import burst
#import Util

# TODO: If running on the robot, user 127.0.0.1 as the address?

burst.init()
print "Controlling the robot at " + burst.ip + ":" + str(burst.port)

import BasicMotion

# Let the user choose an action, perform that action, repeat.
import Commands
from Commands import *

try:
	while True:
		selection = raw_input("> ")
		try:
			x = Commands.CommandParser.parse(selection)
			x.execute()
		except UnsupportedCommand, e:
			print "Error: Unsupported command (" + str(e) + ")."
		except ParseError, e:
			print "Error: Could not parse the command (" + str(e) + ")."
except TerminateSignal:
	pass

burst.shutdown()
