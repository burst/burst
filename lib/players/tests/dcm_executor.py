#!/usr/bin/python

import os
import time
import struct
import numpy

in_tree_dir = os.path.join(os.environ['HOME'], 'src/burst/lib/players')
if os.getcwd() == in_tree_dir:
    # for debugging only - use the local and not the installed burst
    print "DEBUG - using in tree burst.py"
    import sys
    sys.path.insert(0, os.path.join(os.environ['HOME'], 'src/burst/lib'))

import domove_constants
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent
# TODO: Add OnDone on DCM motion sequence finished/cleared
#from burst_util import transpose, cumsum, BurstDeferred

DCM_OFFSET = 5000 #2 seconds - for remote, can be lowered to ~50ms (according to doc it has to be "at least 20 ms")
MS = 1000
# DCM Merge modes
CLEAR_ALL = "ClearAll"
MERGE = "Merge"
CLEAR_AFTER = "ClearAfter"
CLEAR_BEFORE = "ClearBefore"
INTERPOLATION_STEP = 0.025

class DCMExecutor(InitialBehavior):
    
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        self.dcmProxy = burst.getDCMProxy(True)
        self.f = open('interpolated.txt','w')
        self.test()

    def test(self):
        #debug behaviors
        #for count in range(1, 100):
        #    print self.dcmProxy.getTime(0)

        self._world._motion.setBodyStiffness(0.9)
        self._memory = self._world._memory
        self.createMovementJointsAlias()
        self._actions.executeMoveRadians(domove_constants.INITIALPOSJOINTVALUES,1).onDone(self.onDoneInitialPosture)

        #self._actions.executeMoveRadians(domove_constants.INITIALPOSJOINTVALUES,1)
        # self.doOne("Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value", 1.0)
        #t = self.dcmProxy.getTime(0)
        #print "got t = %s" % t
        #ret = self.dcmProxy.set(["Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value", 'ClearAll', [[2.0, t+500]]])
        #print "called dcm.set, got %s" % repr(ret)
    


    def createMovementJointsAlias(self):
        self.dcmProxy.createAlias(["MOVEMENT_JOINTS_L", domove_constants.MOVEMENT_JOINTS_LEFT])
        self.dcmProxy.createAlias(["MOVEMENT_JOINTS_R", domove_constants.MOVEMENT_JOINTS_RIGHT])

    def onDoneInitialPosture(self):
        print "DEBUG: onDoneInitialPosture called"
        #t = self.dcmProxy.getTime(0)
        #self.dcmProxy.set(["Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value", 'ClearAll', [[2.0, t+500]]])
        #self.addMotionSequence((["Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value"], [[2.0]], [[1.0]]))
        #self.dcmProxy.set( ["Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value", 'ClearAll', [[0, t+100]] ])
        self.addMotionSequence(domove_constants.gait_attempt_generate(3.0))
        
        time.sleep(20.0)
        print "DONE"
        self.f.close()
        #self.addMotionSequence(domove_constants.gait_attempt_generate(4.0))        
        #time.sleep(5.0)
        #self.addMotionSequence(domove_constants.gait_attempt_generate(4.0))       
        #time.sleep(5.0)
        #self.addMotionSequence(domove_constants.gait_attempt_generate(4.0))    
        self._world._motion.setBodyStiffness(0.0)
        print "STIFFNESS OFF!"
        
    
    def addMotionSequence(self, (jointCodes, angles, times), mergeMode=CLEAR_ALL):
        """emulates naoQi doMove behavior with linear interpolation + DCM merge mode"""
    
        print "DEBUG: add Motion Sequence called"        
        #import pdb; pdb.set_trace()

        #get current actuators values (ALMemory, good enough):
        self._memory.getListData(jointCodes).addCallback(lambda result: self.ongetListData(result,(jointCodes, angles, times),mergeMode ))


    def ongetListData(self, result,(jointCodes, angles, times), mergeMode):
        initialvalues = result
        #print (initialvalues)
        self.dcmProxy.getTime(0).addCallback(lambda result: self.onGetTime(result,(jointCodes, angles, times),mergeMode,initialvalues ))

    def onGetTime(self, result,(jointCodes, angles, times), mergeMode,initialvalues):
        timeVal = result + DCM_OFFSET #base time
        print "DEBUG: onGetTime called"
        
        for index in range(len(jointCodes)):         
            (iangles, itimes) = self.interpolate(initialvalues[index], (angles[index] , times[index] ))        
            #print [jointCodes[index], mergeMode,
            #    [ [iangles[commandIndex] , int(itimes[commandIndex]*MS + timeVal) ]
            #        for commandIndex in range(len(iangles) ) ]]
  
            # debug
            self.dcmProxy.set([jointCodes[index], mergeMode,
                [ [iangles[commandIndex] , int(itimes[commandIndex]*MS + timeVal) ]
                    for commandIndex in range(len(iangles) ) ]])
        

    def interpolate(self, curangle, (angles, times)):
        """interpolates array by given interpolation parameter (polynom degree)
        """
        returnangles = list()
        returntimes = list()
        #print angles
        #print times
        for index in range(len(angles)):
            if index>0:
                starttime=times[index-1]
                startangle = angles[index-1]
            else:
                starttime=0
                startangle = curangle

            finishtime = times[index]
            timeintervals=int((finishtime-starttime) / INTERPOLATION_STEP)
            eqparams = self.calculatefunction(finishtime-starttime, startangle, angles[index])                    
            
            for i in range (1, timeintervals+1):
                #curtime = starttime + INTERPOLATION_STEP*i
                curtime = INTERPOLATION_STEP*i
                angleval = startangle #d
                #c=0
                x = curtime * curtime
                angleval = angleval+ eqparams[1]*x #b
                x = x * curtime
                angleval = angleval+ eqparams[0]*x #a
                    
                returnangles.append(angleval)  
                returntimes.append(curtime + starttime)
        #debug
        
        #print >>self.f, "initial times:"
        #print >>self.f, [0.0] + times
        #print >>self.f, "Times: "
        #print >>self.f,  returntimes
        #print >>self.f,  "initial angles:"
        #print >>self.f,  [curangle] + angles
        #print >>self.f, "Angles: "
        #print >>self.f, returnangles
        return returnangles,  returntimes

    def calculatefunction(self, t, v1, v2):
        """interpolates ^3 polynom for given two points (assuming f'(x1)=f'(x2)=0
        """
        #debug
        #print "v1 %s, v2 %s, t %s" % (v1,v2,t)
        # calculate t^2
        t_2 = t * t
        # calculate b
        b = (v2-v1)/((1.0/3)*t_2)
        # calculate a
        a = -2*b/(3*t)
        # debug - check data
        #print "v1 %s, v2 %s, t %s, a %s, b %s,  %s, %s" % (v1,v2,t,a,b, 3*t_2*a +2*t*b, t_2*t*a + t_2*b- v2 + v1 )
        return [a,b,0,v1]        
        
if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(DCMExecutor).run()

