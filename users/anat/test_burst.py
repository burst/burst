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

    
    # create proxy
    try:
        alsonarProxy = burst.ALProxy("ALSonar",burst.ip,burst.port)
    except RuntimeError,e:
        print "error while creation alsonar's proxy"
        exit(1)

    # subscribe to ALUltraound
    try:
        period = 2000 # minimum should be 240ms according to documentation
        alsonarProxy.subscribe("test", [ period ] )
        print "subscription to ALSonar is ok" 
    except RuntimeError,e:
        print "error while subscribing to alsonar"
        exit(1)


    # processing
    # ....
    print "processing"

    # ====================
    # Create proxy to ALMemory
    memoryProxy = burst.getMemoryProxy() #could have also used broker.getMemoryProxy()

    # Get The Left Foot Force Sensor Values

    #for i in xrange(1,2000):
    US = memoryProxy.getData("extractors/alsonar/distances",0)

    print US

    #~ # unsubscribe to ALUltraound
    #~ try:
        #~ alsonarProxy.unsubscribe("test")
        #~ print "unsubscription to ALSonar is ok"
    #~ except RuntimeError,e:
        #~ print "error while unsubscribing to alsonar"
        #~ exit(1)

    #~ print "quitting"
    #~ exit(0)
    
    
    
    #print( "Right FSR : %.2f %.2f %.2f %.2f" %  (RFsrFL, RFsrFR, RFsrBL, RFsrBR) )


    
if __name__ == '__main__':
    main()

