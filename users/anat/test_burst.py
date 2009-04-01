#!/usr/bin/env python

import os
import sys # for accessing command line arguments, not required by burst
import time

import burst

def main(ip=None):
    if '--help' in sys.argv or '-h' in sys.argv:
        print burst.default_help()
        raise SystemExit
    kw = {}
    if ip is not None:
        kw['ip'] = ip
    burst.init(**kw) # call once, connects to the naoqi server
    # broker = burst.getBroker()
    # use broker ...


    memoryProxy = burst.getMemoryProxy() #could have also used broker.getMemoryProxy()

    
    # Get The Left Foot Force Sensor Values
    LFsrFL = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value",0)
    LFsrFR = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/Value",0)
    LFsrBL = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/Value",0)
    LFsrBR = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/Value",0)

    print( "Left FSR : %.2f %.2f %.2f %.2f" %  (LFsrFL, LFsrFR, LFsrBL, LFsrBR) )

    # Get The Right Foot Force Sensor Values
    RFsrFL = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/Value",0)
    RFsrFR = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/FrontRight/Sensor/Value",0)
    RFsrBL = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/RearLeft/Sensor/Value",0)
    RFsrBR = memoryProxy.getData("Device/SubDeviceList/RFoot/FSR/RearRight/Sensor/Value",0)

    print( "Right FSR : %.2f %.2f %.2f %.2f" %  (RFsrFL, RFsrFR, RFsrBL, RFsrBR) )


    
if __name__ == '__main__':
    main()

