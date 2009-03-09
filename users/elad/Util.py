import os, sys, time


def runningOnRobot():
	return open('/etc/hostname').read().strip().lower() in ['messi', 'gerrard', 'hagi']
	
	
class StringTokenizer(object):
	def __init__(self,source):
		self.source = source
		self.currentPosition = 0;
		while self.currentPosition < len(source) and source[self.currentPosition] == ' ':
			self.currentPosition += 1
	
	def nextToken(self):
		if self.currentPosition < len(self.source):
			start = self.currentPosition
			while self.currentPosition < len(self.source) and self.source[self.currentPosition] != ' ':
				self.currentPosition += 1
			end = self.currentPosition
			while self.currentPosition < len(self.source) and self.source[self.currentPosition] == ' ':
				self.currentPosition += 1
			return self.source[start:end]
			
	def hasMoreTokens(self):
		return self.currentPosition < len(self.source)
