import Robot
import Util
from Util import *
import BasicMotion


class Command(object):	
	keywords = []
	
	name = ""
	
	@classmethod
	def triggeredBy(clazz, command):
		return command.split(" ")[0] in clazz.keywords

	def __init__(self, command):
		self.command = command
	
	def execute(self):
		pass

	def __str__(self):
		return "I am a command that's triggered by the following keywords: " + str(self.__class__.keywords)


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
		Robot.getSpeechProxy().say(self.command[3:])


class StiffnessOnCommand(Command):
	"stiffness_on"
	
	__metaclass__ = Registrat
	
	keywords = ["stiffness_on", "stiffnesson", "son"]

	def execute(self):
		BasicMotion.setStiffness(1.0)


class StiffnessOffCommand(Command):
	"stiffness_off"
	
	__metaclass__ = Registrat

	keywords = ["soff", "sof", "soft", "stiffness_off", "stiffnessoff"]

	def execute(self):
		BasicMotion.setStiffness(0.0)


class WalkCommand(Command):
	"walk"
	
	__metaclass__ = Registrat
	
	keywords = ["w", "walk"]
	
	def execute(self): # TODO: Fix.
		stringTokenizer = StringTokenizer(self.command[5:])
		distance = float(stringTokenizer.nextToken())
		if not stringTokenizer.hasMoreTokens():
			BasicMotion.slowStraightWalk(distance)
		else:
			gait = stringTokenizer.nextToken()
			if gait in ["slow", "slowly", "s"]:
				BasicMotion.slowStraightWalk(distance)
			elif gait in ["fast", "f", "quick", "quickly", "q"]:
				BasicMotion.fastStraightWalk(distance)
			else:
				print "Unsupport gait. Choose either slow, fast, or leave empty to default to slow."
				

class CrouchPositionCommand(Command):
	"crouch"
	
	__metaclass__ = Registrat
	
	keywords = ["crouch", "c"]
	
	def execute(self):
		#BasicMotion.crouch() # Unimplemented.
		pass


class ZeroPositionCommand(Command):
	"zero (position)"
	
	__metaclass__ = Registrat
	
	keywords = ["0", "z", "zero"]
	
	def execute(self):
		BasicMotion.zeroPosition()


class InitPositionCommand(Command):
	"initial (position)"
	
	__metaclass__ = Registrat
	
	keywords = ["init", "i", "initial", "initial position"]
	
	def execute(self):
		BasicMotion.initPosition()


class ShootCommand(Command):
	"shoot"
	
	__metaclass__ = Registrat
	
	keywords = ["shoot"]
	
	def execute(self):
		import Shoot
		Shoot.do()

class ExitCommand(Command):
	"exit"
	
	__metaclass__ = Registrat

	keywords = ["exit", "quit", "q", "e"]
	
	def execute(self):
		raise TerminateSignal()


class CommandParser(object):
	
	commands = [SayCommand, StiffnessOnCommand, StiffnessOffCommand, WalkCommand, CrouchPositionCommand, ZeroPositionCommand, 
		InitPositionCommand, ExitCommand, HelpCommand, ShootCommand]

	@classmethod	
	def parseSingleCommand(clazz, userCommand):
		keyword = userCommand.split(" ")[0]
		for command in clazz.commands:
			if command.triggeredBy(keyword):
				return command(userCommand)
		raise UnsupportedCommand()
		
	@classmethod	
	def parseCompoundCommand(clazz, userCommand):
		
		
		pass
		

