import os, sys, time
import pygame

# Initialization:
pygame.init()
pygame.joystick.init()
j = pygame.joystick.Joystick(0)
j.init()

class JoystickWrapper(object):
	def __init__(self, x_axis=0, y_axis=1):
		self.x_axis = x_axis
		self.y_axis = y_axis
		pygame.init() # It's safe to call this method multiple times. # TODO: My memory deceived me - it doesn't specify if it is.
		pygame.joystick.init() # It's safe to call this method multiple times.
		self.joystick = pygame.joystick.Joystick(0) # Assumes one joystick in the system, I guess.
	
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
		

def run():
	joystick = JoystickWrapper(0,1)
	Robot.init()
	while True:
#		time.sleep(0.1)
#		print joystick.get_coordinates()
		time.sleep(5)
