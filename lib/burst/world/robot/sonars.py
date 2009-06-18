#!/usr/bin/python

from burst_consts import LEFT, RIGHT
from burst import events as events_module
from burst.events import (EVENT_SONAR_OBSTACLE_SEEN, EVENT_SONAR_OBSTACLE_LOST, EVENT_SONAR_OBSTACLE_IN_FRAME)
from burst_util import RingBuffer
import burst

HISTORY_SIZE = 4 # size of history buffer (500ms * 4 frames = ~1 second)
# TEMP  - USE LARGER DISTANCE FOR WEBOTS TESTSING!!!
#NEAR_DISTANCE = 0.6
NEAR_DISTANCE = 0.4 # distance in meters

__all__ = ['Sonars']

# TODO: When several robots are next to each other, do their sonars collide?
# TODO: What to do when events jump between left & right?
# TODO: What to do when on the edge of distance (keeps getting same event)
# TODO: Store distance somewhere?
class Sonars(object):

    _var = "extractors/alultrasound/distances"

    def __init__(self, world):
        if burst.options.run_ultrasound:
            world._ultrasound.post.subscribe('', [500])
            world.addMemoryVars([Sonars._var])
        self._world = world
        self._sonarHistory = RingBuffer(HISTORY_SIZE)
        self._obstacleSeen = False
        self._lastReading = None

    # valid only when obstacle seen/in_frame events occur, otherwise, returns None
    def getLastReading(self):
        return self._lastReading

    def readSonarDistances(self, data):
#        print "SONAR: LEFT Got %f" % (data[LEFT])
#        print "SONAR: RIGHT Got %f" % (data[RIGHT])
        self._sonarHistory.ring_append([data[LEFT], data[RIGHT]])

    def calc_events(self, events, deferreds):
        if not burst.options.run_ultrasound:
            return
        
        new_data = self._world.vars[Sonars._var]
        #print "new_data:", new_data
        # make sure sonar data is valid
        if new_data and (len(new_data) >= 2):
            self.readSonarDistances(new_data)

            newEvent = None
            # if at least one reading shows an obstacle, do more complex analysis
            if min(new_data[LEFT], new_data[RIGHT]) < NEAR_DISTANCE:
                self._lastReading = self.calcObstacleFromSonar(self._sonarHistory)

                if self._obstacleSeen:
                    newEvent = EVENT_SONAR_OBSTACLE_IN_FRAME
                    #print "SONAR: IN_FRAME obstacle (on %s, distance of %f)" % (self._lastReading)
                else:
                    # new obstacle found, report it
                    newEvent = EVENT_SONAR_OBSTACLE_SEEN
                    #print "SONAR: SEEN obstacle (on %s, distance of %f)" % (self._lastReading)
                self._obstacleSeen = True
            else:
                if self._obstacleSeen:
                    newEvent = EVENT_SONAR_OBSTACLE_LOST
                    self._obstacleSeen = False
                    #print "SONAR: LOST obstacle (last seen on %s, distance of %f)" % (self._lastReading)
                self._lastReading = None

            if (newEvent != None):
                events.add(newEvent)
        else:
            print "SONAR: No reading?! ignoring..."
            self._lastReading = None

    ##
    # Authors: Sonia Anshtein Shafran & Rony Fragin.
    # Input: Sonar history
    # Each sample is an array of 2 - left and right readings.
    # Output: Array of 2 - evaluation of both direction of object and its distance.
    
    def calcObstacleFromSonar(self, history):
        # Initialize variables.
        vote_thresh_left= 0
        vote_thresh_right= 0
        vote_majority_left= 0
        vote_majority_right= 0
        diff= 9999
        min_left= 9999
        min_right= 9999
        upper_thresh= 1.0
        lower_thresh= 0.045
    
        # Run on data and get the needed parameters for evaluation.
        for point in history:
            if point == None:
                break
            left_val = point[LEFT]
            right_val = point[RIGHT]
        
            currDiff= abs(left_val-right_val)
            # New minimal difference between left and right readings.
            if currDiff<diff:
                # Readings of an existing object [ below the threshold ].
                if left_val<=upper_thresh or right_val<=upper_thresh:
                    # Some weird bug when left and right readings are the same. 
                    if currDiff>0:
                        diff= currDiff;
            # New left minimum reading.
            if left_val<min_left:
                min_left= left_val
            # New right minimum reading.
            if right_val<min_right:
                min_right= right_val
            # Left reading was below upper threshold - valid.
            if left_val<upper_thresh:
                # Threshold voting counts the number of times we
                # got a valid reading from the sensor.
                vote_thresh_left= vote_thresh_left + 1
            # Right reading was below upper threshold - valid.
            if right_val<upper_thresh:
                vote_thresh_right= vote_thresh_right + 1
            # Left value was lower than the right value.
            if left_val<=right_val:
                # Majority voting counts the number of times a
                # reading of one sensor was lower than the other's.
                vote_majority_left= vote_majority_left + 1
            # Right value was lower than the left value.
            if right_val<=left_val:
                vote_majority_right= vote_majority_right + 1
        
        # Find min of min.
        if min_left<min_right:
            min_min= min_left
        else:
            min_min= min_right
        
        # If min of min is above upper threshold, 
        # the reading is invalid.
        if min_min>upper_thresh:
            return ("nothing", 0)
        else:
            # If minimal difference is below lower threshold,
            # the direction is center.
            if diff<lower_thresh:
                return ("center", min_min)
            else:
                # If more threshold votes were cast to the left,
                # meaning left direction is dominent.
                if vote_thresh_left>vote_thresh_right:
                    return ("left", min_min)
                # If more threshold votes were cast to the right,
                # meaning right direction is dominent.
                elif vote_thresh_left<vote_thresh_right:
                    return ("right", min_min)
                # Both sides got the same amount of threshold votes.
                else:
                    # If more majority votes were cast to the left,
                    # meaning left direction is dominent.
                    if vote_majority_left>vote_majority_right:
                        return ("left", min_min)
                    # If more majority votes were cast to the right,
                    # meaning right direction is dominent.
                    elif vote_majority_left<vote_majority_right:
                        return ("right", min_min)
                    # No majority to any side, center is dominent.
                    else:
                        return ("center", min_min)
