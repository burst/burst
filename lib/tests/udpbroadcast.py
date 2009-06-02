#!/usr/bin/python

import socket, traceback
from time import sleep

host = ''                               # Bind to all interfaces
port = 3838

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))

while 1:
    s.sendto("I am here", ('255.255.255.255', 3838))
    sleep(1.0)

