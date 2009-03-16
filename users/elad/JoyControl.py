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
		return self.joystick.get_axis(self.y_axis)
	
	def isButtonPressed(self, buttonNumber, upToDate=False):
		if not upToDate:
			self.__class__.update()
		return self.joystick.get_button(buttonNumber) == 1
				

def run():
	walking = False
	joystick = JoystickWrapper(0,1)
	Robot.init()
	while True:
		if joystick.isButtonPressed(closeButton):
			BasicMotion.stopWalking()
			walking = False
			break
		if joystick.isButtonPressed(shootButton):
			#BasicMotion.wait(BasicMotion.stopWalking())
			BasicMotion.stopWalking() # TODO
			import Shoot
			Shoot.do()			
		x, y = joystick.get_x(), joystick.get_y() # TODO
		if abs(x) < threshold and abs(y) < threshold:
			BasicMotion.stopWalking()
			walking = False
		elif abs(y) > threshold:
			if not walking:
				walking = True
				BasicMotion.slowStraightWalk(1.0)
			else:
				BasicMotion.addWalkStraight(0.1, 60)
	Robot.shutdown()

run()
