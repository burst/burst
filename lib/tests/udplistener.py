#!/usr/bin/python

"""
Tester for GameController
"""

from socket import *

s = socket(AF_INET,SOCK_DGRAM)

s.bind(('0.0.0.0', 3838))

while True:
    print s.recvfrom(100)

