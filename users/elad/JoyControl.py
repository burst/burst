import os, sys, time
import pygame
import Robot
import BasicMotion

# Constants:
threshold = 0.5
shootButton = 0
closeButton = 1

# Initialization:
pygame.init()
pygame.joystick.init()

class JoystickWrapper(object):
	def __init__(self, x_axis=0, y_axis=1):
		self.x_axis = x_axis
		self.y_axis = y_axis
		pygame.init() # It's safe to call this method multiple times. # TODO: My memory deceived me - it doesn't specify if it is.
		pygame.joystick.init() # It's safe to call this method multiple times.
		self.joystick = pygame.joystick.Joystick(0) # Assumes one joystick in the system, I guess.
		self.joystick.init()
	
	@classmethod
	def update(cls):
		pygame.event.poll() # Updates the joystick to the current status.
	
	def get_coordinates(self):
		return (self.get_x(), self.get_y())
		
	def get_x(self, upToDate=False):
		if not upToDate:
			self.__class__.update()
		return self.joystick.get_axis(self.x_axis)

	def get_y(self, upToDate=False):
		if not upToDate:
			self.__class__.update()
		return -self.joystick.get_axis(self.y_axis)
	
	def isButtonPressed(self, buttonNumber, upToDate=False):
		if not upToDate:
			self.__class__.update()
		return self.joystick.get_button(buttonNumber) == 1
	
	def getStatus(self):
		return JoystickStatus(self)
	
	def count_buttons(self):
		return self.joystick.get_numbuttons()

class JoystickStatus(object):
	def __init__(self, joystick):
		self.joystick = joystick
		self.buttons = joystick.count_buttons() * [False]
		self.update()
	
	def update(self):
		pygame.event.poll()
		self.x = self.joystick.get_x(True)
		self.y = self.joystick.get_y(True)
		i = 0
		for i in range(len(self.buttons)):
			self.buttons[i] = self.joystick.isButtonPressed(i, True)
	
	
def run():
	print "eek"
	robotStatus = "at rest"
	joystick = JoystickWrapper(0,1)
	Robot.init()
	joystickStatus = joystick.getStatus()

	while True:
		joystickStatus.update()
		# Exit
		if joystickStatus.buttons[closeButton]:
			if "walking" in robotStatus or "turning" in robotStatus:
				BasicMotion.stopWalking()
			robotStatus = "exiting"
			break
		# Shooting:
		elif joystickStatus.buttons[shootButton] and abs(joystickStatus.y) < threshold and abs(joystickStatus.x) < threshold:
			if "walking" in robotStatus or "turning" in robotStatus:
				BasicMotion.stopWalking()
			BasicMotion.shoot()
		# Stop walking:
		if abs(joystickStatus.x) < threshold and abs(joystickStatus.y) < threshold:
			if "walking" in robotStatus or "turning" in robotStatus:
				BasicMotion.stopWalking()
			robotStatus = "at rest"
		# Walk forwards:
		elif joystickStatus.y > threshold and abs(joystickStatus.x) < threshold:
			if robotStatus == "walking forwards":
				BasicMotion.addWalkStraight(0.1, 60)
			else:
				if "walking" in robotStatus or "turning" in robotStatus:
					BasicMotion.stopWalking()
				BasicMotion.slowStraightWalk(1.0)
			robotStatus = "walking forwards"
		# Walk backwards:
		elif joystickStatus.y < -threshold and abs(joystickStatus.x) < threshold:
			if robotStatus == "walking backwards":
				BasicMotion.addWalkStraight(-0.1, 60)
			else:
				if "walking" in robotStatus or "turning" in robotStatus:
					BasicMotion.stopWalking()
				BasicMotion.slowStraightWalk(-1.0)
			robotStatus = "walking backwards"
		# Turn right:
		elif abs(joystickStatus.y) < threshold and joystickStatus.x > threshold:
			if robotStatus == "turning right":
				BasicMotion.addTurn(-1.0)
			else:
				if "walking" in robotStatus or "turning" in robotStatus:
					BasicMotion.stopWalking()
				BasicMotion.turn(-1.0)
			robotStatus = "turning right"
		# Turn left:
		elif abs(joystickStatus.y) < threshold and joystickStatus.x < -threshold:
			if robotStatus == "turning left":
				BasicMotion.addTurn(1.0)
			else:
				if "walking" in robotStatus or "turning" in robotStatus:
					BasicMotion.stopWalking()
				BasicMotion.turn(1.0)
			robotStatus = "turning left"


			robotStatus = "shooting"
		# In either case, go to sleep for a while, so it's not THAT bad of a busy-wait.
		time.sleep(0.001)
		
	Robot.shutdown()	


run()
