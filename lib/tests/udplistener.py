#!/usr/bin/python

"""
Tester for GameController
"""

from socket import *

import sys
bind_host = '0.0.0.0' # 'any' interface
bind_port = 3838
if len(sys.argv) > 1:
    bind_host = sys.argv[1]

s = socket(AF_INET,SOCK_DGRAM)

print "binding to %s:%s" % (bind_host, bind_port)
s.bind((bind_host, bind_port))

while True:
    print s.recvfrom(100)

