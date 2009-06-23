import os, sys, time


def runningOnRobot():
	return open('/etc/hostname').read().strip().lower() in ['messi', 'gerrard', 'hagi']


class StringTokenizer(object):
	def __init__(self, source):
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

	@staticmethod
	def tokenize(string):
		result = []
		tokenizer = StringTokenizer(string)
		while tokenizer.hasMoreTokens():
			result.append(tokenizer.nextToken())
		return result


def findClosingPara(string):
	i = 1
	acc = 1
	while i < len(string):
		if string[i] == "(":
			acc += 1
		elif string[i] == ")":
			acc -= 1
		if acc == 0:
			return i
		i += 1
	raise Exception # TODO: "No matching paranthesis."
