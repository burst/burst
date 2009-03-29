#!/usr/bin/env python

from time import sleep
import sys
sys.path.append('../')

def main():
    import burst
    if '--help' in sys.argv or '-h' in sys.argv:
        print default_help()
        raise SystemExit
    burst.init()
    broker = burst.getBroker()
    from bodyposition import BodyPosition
    bp = BodyPosition(broker=broker)
    while True:
        bp.update()
        bp.pprint()
        sleep(0.1)

if __name__ == '__main__':
    main()

