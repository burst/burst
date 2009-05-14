#!/usr/bin/python

import socket
import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        raise Exception("What port?")
    port = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',0))
    s.connect(('localhost',port))
    s.send("3 4\n")
    print "Connected on", s.getsockname()[1]
    while True:
        print s.recv(200),
        sys.stdout.flush()

