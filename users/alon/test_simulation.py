from time import sleep

import burst
from burst import naoqi

def main():
    if burst.ip is None or burst.port is None:
        print burst.default_help()
        raise SystemExit
    broker = naoqi.ALBroker("test_simulation", "127.0.0.1", 9999, burst.ip, burst.port)
    from bodyposition import BodyPosition
    bp = BodyPosition(broker=broker)
    while True:
        bp.update()
        bp.pprint()
        sleep(0.1)

if __name__ == '__main__':
    main()

