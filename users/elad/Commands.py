import Robot
import Util
from Util import *
import BasicMotion


class Command(object):
	""
	
	keywords = []
	
	pid = None
	
	@classmethod
	def triggeredBy(clazz, command):
		return command.split(" ")[0] in clazz.keywords

	def __init__(self, command):
		self.command = command
	
	def execute(self):
		pass
		
	def wait(self):
		pass
	
	# DBG
	def toString(self):
		return self.command


class CompoundCommand(object):
	""
	
	def __init__(self, commands, isSynchronous):
		self.commands = commands
		self.isSynchronous = isSynchronous
	
	def execute(self):
		for command in self.commands:
			command.execute()
			if self.isSynchronous:
				command.wait()

	def wait(self):
		if not self.isSynchronous: # Otherwise, you've already waited when executing.
			for command in self.commands:
				command.wait()
	
	# DBG
	def toString(self):
		string = "["
		if len(self.commands) > 0:
			string += self.commands[0].toString()
		i = 1
		while i < len(self.commands):
			string += ", " + self.commands[i].toString()
			i += 1
		return string + "]"


class TerminateSignal(Exception):
	pass


class UnsupportedCommand(Exception):
	pass


class ParseError(Exception):
	pass


class Registrat(type):
	registered = []
	def __new__(cls, name, bases, dct):
		clazz = type.__new__(cls, name, bases, dct)
		Registrat.registered.append(clazz)
		return clazz

class HelpCommand(Command):
	"help"
	
	__metaclass__ = Registrat
	
	keywords = ["help", "command", "commands", "list", "h", "?"]
	
	def execute(self):
		for command in Registrat.registered:
			print command.__doc__.center(20) + " " + str(command.keywords)
			
			
class SayCommand(Command):
	"say"
	
	__metaclass__ = Registrat

	keywords = ["say"]
	
	def execute(self):
		self.pid = Robot.getSpeechProxy().post.say(self.command[3:]) # TODO: Should pass through some other module.
	
	def wait(self):
		Robot.getSpeechProxy().wait(self.pid)


class StiffnessOnCommand(Command):
	"stiffness_on"
	
	__metaclass__ = Registrat
	
	keywords = ["stiffness_on", "stiffnesson", "son"]

	def execute(self):
		self.pid =  BasicMotion.setStiffness(1.0)
	
	def wait(self):
		BasicMotion.wait(self.pid)


class StiffnessOffCommand(Command):
	"stiffness_off"
	
	__metaclass__ = Registrat

	keywords = ["soff", "sof", "soft", "stiffness_off", "stiffnessoff"]

	def execute(self):
		self.pid = BasicMotion.setStiffness(0.0)
	
	def wait(self):
		BasicMotion.wait(self.pid)


class WalkCommand(Command):
	"walk"
	
	__metaclass__ = Registrat
	
	keywords = ["w", "walk"]
	
	def execute(self): # TODO: Fix.
		stringTokenizer = StringTokenizer(self.command[5:])
		distance = float(stringTokenizer.nextToken())
		if not stringTokenizer.hasMoreTokens():
			self.pid = BasicMotion.slowStraightWalk(distance)
		else:
			gait = stringTokenizer.nextToken()
			if gait in ["slow", "slowly", "s"]:
				self.pid = BasicMotion.slowStraightWalk(distance)
			elif gait in ["fast", "f", "quick", "quickly", "q"]:
				self.pid = BasicMotion.fastStraightWalk(distance)
			else:
				print "Unsupport gait. Choose either slow, fast, or leave empty to default to slow."
	
	def wait(self):
		BasicMotion.wait(self.pid)
				

class CrouchPositionCommand(Command):
	"crouch"
	
	__metaclass__ = Registrat
	
	keywords = ["crouch", "c"]
	
	def execute(self):
		#return BasicMotion.crouch() # Unimplemented.
		pass


class ZeroPositionCommand(Command):
	"zero (position)"
	
	__metaclass__ = Registrat
	
	keywords = ["0", "z", "zero"]
	
	def execute(self):
		self.pid = BasicMotion.zeroPosition()
	
	def wait(self):
		BasicMotion.wait(self.pid)


class InitPositionCommand(Command):
	"initial (position)"
	
	__metaclass__ = Registrat
	
	keywords = ["init", "i", "initial", "initial position"]
	
	def execute(self):
		self.pid = BasicMotion.initPosition()
	
	def wait(self):
		BasicMotion.wait(self.pid)


# TODO: Violates synchronicity?
class ShootCommand(Command):
	"shoot"
	
	__metaclass__ = Registrat
	
	keywords = ["shoot"]
	
	def execute(self): # TODO: Return pid.
		import Shoot
		Shoot.do()


class ExitCommand(Command):
	"exit"
	
	__metaclass__ = Registrat

	keywords = ["exit", "quit", "q", "e"]
	
	def execute(self):
		raise TerminateSignal()
		

class FlexArmCommand(Command):
	"flex"
	
	__metaclass__ = Registrat
	
	keywords = ["flex"]
	
	def execute(self):
		if "l" in self.command:
			self.pid = BasicMotion.flexLeftArm()
		elif "r" in self.command:
			self.pid = BasicMotion.flexRightArm()
		else:
			raise ParseError
		
	def wait(self):
		BasicMotion.wait(self.pid)


class UnflexArmCommand(Command):
	"unflex"
	
	__metaclass__ = Registrat
	
	keywords = ["unflex"]
	
	def execute(self):
		if "l" in self.command:
			self.pid = BasicMotion.unflexLeftArm()
		elif "r" in self.command:
			self.pid = BasicMotion.unflexRightArm()
		else:
			raise ParseError
	
	def wait(self):
		BasicMotion.wait(self.pid)


class CloseHandCommand(Command):
	"close_hand"
	
	__metaclass__ = Registrat
	
	keywords = ["closehand", "handclose", "close_hand", "hand_close", "ch"]
	
	def execute(self):
		if "l" in self.command:
			self.pid = BasicMotion.closeLeftHand()
		elif "r" in self.command:
			self.pid = BasicMotion.closeRightHand()
		else:
			raise ParseError
	
	def wait(self):
		BasicMotion.wait(self.pid)


class OpenHandCommand(Command):
	"open_hand"
	
	__metaclass__ = Registrat
	
	keywords = ["openhand", "handopen", "open_hand", "hand_open", "oh"]
	
	def execute(self):
		if "l" in self.command:
			self.pid = BasicMotion.openLeftHand()
		elif "r" in self.command:
			self.pid = BasicMotion.openRightHand()
		else:
			raise ParseError

	def wait(self):
		BasicMotion.wait(self.pid)


class CommandParser(object):
	
	commands = Registrat.registered

	@classmethod
	def parseSingleCommand(clazz, userCommand):
		userCommand = userCommand.strip()
		keyword = userCommand.split(" ")[0]
		for command in clazz.commands:
			if command.triggeredBy(keyword):
				return command(userCommand)
		print userCommand
		raise UnsupportedCommand()

	@classmethod
	def parseCompoundCommand(clazz, userCommand):
		
		sync = False
		coms = []
		
		userCommand = userCommand.strip()
		while userCommand != "":
			userCommand = userCommand.strip()
#			print "userCommand = " + userCommand
			if userCommand == "":
				break
			elif userCommand[0] == "(":
				closing = Util.findClosingPara(userCommand)
				coms.append(CommandParser.parseCompoundCommand(userCommand[1:closing]))
				userCommand = userCommand[closing+1:]
			elif ("|" in userCommand) or ("&" in userCommand):
				delimiter1 = userCommand.find("|")
				delimiter2 = userCommand.find("&")
				if delimiter1 == -1:
					delimiter = delimiter2
				elif delimiter2 == -1:
					delimiter = delimiter1
				else:
					delimiter = min(delimiter1, delimiter2)
				if userCommand[delimiter] == "&":
					sync = True
				if delimiter != 0:
					coms.append(CommandParser.parseCompoundCommand(userCommand[0:delimiter]))
				userCommand = userCommand[delimiter+1:]
			else:
				coms.append(CommandParser.parseSingleCommand(userCommand))
				userCommand = ""
		
		return CompoundCommand(coms, sync)
	
	@classmethod
	def parse(clazz, userCommand):
		return CommandParser.parseCompoundCommand(userCommand)
		
# son & 0 & (openhand right | openhand left | say opening) & (i | closehand right | closehand left) & sof
