#!/usr/bin/env python
from time import sleep
import sys

from burst import ALBroker, default_help, ip, port

def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print default_help()
        raise SystemExit
    broker = ALBroker("test_simulation", "127.0.0.1", 9999, ip, port)
    from bodyposition import BodyPosition
    bp = BodyPosition(broker=broker)
    while True:
        bp.update()
        bp.pprint()
        sleep(0.1)

if __name__ == '__main__':
    main()

