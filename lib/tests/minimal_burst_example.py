#!/usr/bin/env python

import sys # for accessing command line arguments, not required by burst
import burst

def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print burst.default_help()
        raise SystemExit
    burst.init() # call once, connects to the naoqi server
    broker = burst.getBroker()
    # use broker ...

if __name__ == '__main__':
    main()

