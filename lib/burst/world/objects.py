from math import cos, sin, sqrt, pi, fabs, atan, atan2

from ..consts import (BALL_REAL_DIAMETER, DEG_TO_RAD,
    MISSING_FRAMES_MINIMUM, MIN_BEARING_CHANGE,
    MIN_DIST_CHANGE, GOAL_POST_DIAMETER)
from ..events import (EVENT_BALL_IN_FRAME,
    EVENT_BALL_BODY_INTERSECT_UPDATE, EVENT_BALL_LOST,
    EVENT_BALL_SEEN, EVENT_BALL_POSITION_CHANGED)
from burst_util import running_median, RingBuffer

class Locatable(object):
    """ stupid name. It is short for "something that can be seen, holds a position,
    has a limited velocity which can be estimated, and is also interesting to the
    soccer game"

    Because of the way the vision system we use (northern's) works, we keep things
    in polar coordinates - bearing in radians, distance in centimeters.
    """
    
    _name = "Locatable" # override to get nicer %s / %r

    REPORT_JUMP_ERRORS = False
    HISTORY_SIZE = 10

    def __init__(self, world, real_length):
        """
        real_length - [cm] real world largest diameter of object.
        memory, motion - proxies to ALMemory and ALMotion respectively.
        """
        self._world = world
        # cached proxies
        self._memory = world._memory
        self._motion = world._motion
        # longest arc across the object, i.e. a diagonal.
        self._real_length = real_length

        self.history = RingBuffer(Locatable.HISTORY_SIZE) # stores history for last 

        # This is the player body frame relative bearing. radians.
        self.bearing = 0.0
        self.elevation = 0.0
        # This is the player body frame relative distance. centimeters.
        self.dist = 0.0
        self.newness = 0.0 # time of current update
        # previous non zero values
        self.last_bearing = 0.0
        self.last_dist = 0.0
        self.last_elevation = 0.0
        self.last_newness = 0.0 # time of previous update
        # Body coordinate system: x is to the right (body is the torso, and generally
        # the forward walk direction is along the y axis).
        self.body_x = 0.0
        self.body_y = 0.0
        # This is the world x coordinate. Our x axis is to the right of our goal
        # center, and our y is towards the enemy gate^H^H^Hoal. The enemy goal is up.
        # (screw Ender)
        self.x = 0.0
        self.y = 0.0

        # upper barrier on speed, used to remove outliers. cm/sec
        self.upper_v_limit = 400.0
        
        self.seen = False
        self.missingFramesCounter = 0
        
        self.distSmoothed = 0.0
        self.distRunningMedian = running_median(3) # TODO: Change to ballEKF/ballLoc?
        self.distRunningMedian.next()

    HISTORY_LABELS = ['time', 'distance', 'bearing']
    def _record_current_state(self):
        """ pushes new values into the history buffer. called from
        update_location_body_coordinates
        """
        self.history.ring_append([self.newness, self.dist, self.bearing])

    def compute_location_from_vision(self, vision_x, vision_y, width, height):
        mat = self._motion.getForwardTransform('Head', 0) # TODO - can compute this here too. we already get the joints data. also, is there a way to join a number of soap requests together? (reduce latency for debugging)
        radius = max(width, height)
        radius / self._real_length
        # TODO - NOT FINISHED
        #import pdb; pdb.set_trace()

    def update_location_body_coordinates(self, new_dist, new_bearing, new_elevation):
        """ We only update the values if the move looks plausible.
        
        TODO: This is a first order computation of velocity and position,
        removing outright outliers only. To be upgraded to a real localization
        system (i.e. reuse northern's code as a module, export variables).
        """
        newness = self._world.time
        dt = newness - self.newness
        if dt < 0.0:
            print "GRAVE ERROR: time flows backwards, pigs fly, run for your life!"
            raise SystemExit
        body_x, body_y = new_dist * sin(new_bearing), new_dist * cos(new_bearing)
        dx, dy = body_x - self.body_x, body_y - self.body_y
        if dx**2 + dy**2 > (dt * self.upper_v_limit)**2:
            # no way this body jumped that quickly
            if self.REPORT_JUMP_ERRORS:
                print "JUMP ERROR: %s:%s - %s, %s -> %s, %s - bad new position value, not updating" % (
                    self.__class__.__name__, self._name, self.body_x, self.body_y, body_x, body_y)
            return
            
        self.last_newness, self.last_dist, self.last_elevation, self.last_bearing = (
            self.newness, self.dist, self.elevation, self.bearing)

        self.bearing = new_bearing
        self.dist = new_dist
        self._record_current_state()
        self.distSmoothed = self.distRunningMedian.send(new_dist)
        #if isinstance(self, Ball):
        #    print "%s: self.dist, self.distSmoothed: %3.3f %3.3f" % (self, self.dist, self.distSmoothed)
        
        self.elevation = new_elevation
        self.newness = newness
        self.body_x, self.body_y = body_x, body_y
        self.vx, self.vy = dx/dt, dy/dt
    
    def __str__(self):
        return "<%s at %s>" % (self._name, id(self))

class Movable(Locatable):
    def __init__(self, world, real_length):
        super(Movable, self).__init__(world, real_length)

class Ball(Movable):

    _name = 'Ball'

    DEBUG_INTERSECTION = False

    def __init__(self, world):
        super(Ball, self).__init__(world,
            real_length=BALL_REAL_DIAMETER)
        self._ball_vars = ['/BURST/Vision/Ball/%s' % s for s in "bearing centerX centerY confidence dist elevation focDist height width".split()]
        self._world.addMemoryVars(self._ball_vars)

        self.centerX = 0.0
        self.centerY = 0.0
        self.confidence = 0.0
        self.focDist = 0.0
        self.height = 0.0
        self.width = 0.0
        self.body_isect = None
        self.base_point = None
        self.base_point_index = None
    
    #for robot body when facing the other goal
    def compute_intersection_with_body(self):
        
        T = 0
        DIST = 1
        BEARING = 2
        
        X = 1
        Y = 2
        
        ERROR_VAL_X = 3
        ERROR_VAL_Y = 0
        HISTORY_NUM_POINTS = 10 #history->meaning self.history
        
        #vars for least mean squares
        sumX = 0
        sumXY = 0
        sumY = 0
        sumSqrX = 0
        
        if self.history[0] != None:
            self.base_point = [self.history[0][T] , self.history[0][DIST] * cos(self.history[0][BEARING]) , self.history[0][DIST] * sin(self.history[0][BEARING])]
            self.base_point_index = 1
            last_point = self.base_point
            sumX += last_point[X]
            sumXY += last_point[X] * last_point[Y]
            sumY += last_point[Y]
            sumSqrX +=  last_point[X] * last_point[X]
        else:
            return False
        
        n = 0
        for point in self.history:
            if point != None:
                if n == 0:
                    n += 1
                    continue #first point was calc already
                if n <= self.base_point_index:
                    n += 1
                    continue #skipping nonrelevant point
                n += 1
                cor_point = [point[T] , point[DIST] * cos(point[BEARING]) , point[DIST] * sin(point[BEARING])]
                if cor_point[X] > (last_point[X] + ERROR_VAL_X): #checking if not moving toward our goalie
                    self.base_point = cor_point
                    self.base_point_index = n
                    return False 
                sumX += cor_point[X]
                sumXY += cor_point[X] * cor_point[Y]
                sumY += cor_point[Y]
                sumSqrX +=  cor_point[X] * cor_point[X]
            else:
                if n < 5: #TODO: need some kind of col' for diffrent speeds....
                    return False
                break
        
        n = n - self.base_point_index #real number of valid points
        
        
        if n > 4 and fabs((sumX * sumX) - (n * sumSqrX))  >  ERROR_VAL_X: #TODO: need some kind of col' for diffrent speeds....
            #Least mean squares:
            self.body_isect = ((sumX * sumXY) - (sumY * sumSqrX)) / ((sumX * sumX) - (n * sumSqrX))
            
            #print "ball intersection with body: " , self.body_isect
            return True
        return False 
                 
    
    
    
        """
        
        
        if self.history[0] != None:
            self.base_point = [self.history[0][T] , self.history[0][DIST] * cos(self.history[0][BEARING]) , self.history[0][DIST] * sin(self.history[0][BEARING])]
            self.base_point_index = 1
        else:
            return False
       
        i = 0
        for point in self.history:
            if point != None:
                i = i +1
                cor_point = [point[T] , point[DIST] * cos(point[BEARING]) , point[DIST] * sin(point[BEARING])]
                if i > self.base_point_index :
                    if  cor_point[X] - self.base_point[X] > ERROR_VAL_X:
                        self.base_point = cor_point
                        self.base_point_index = i
                        return False
                    if fabs(self.base_point[X] - cor_point[X]) > ERROR_VAL_X and fabs(self.base_point[Y] - cor_point[Y]) > ERROR_VAL_Y and self.base_point[X] > cor_point[X]:
                        m= (self.base_point[Y] - cor_point[Y]) / (self.base_point[X] - cor_point[X])
                        y = cor_point[Y] - m * cor_point[X]
                        self.body_isect = y
                        print "------------------------------------------------"
                        print "cor_x=", cor_point[X], "  base_x=", self.base_point[X], "  cor_y=", cor_point[Y], "  base_y=", self.base_point[Y]
                        print "------------------------------------------------"
                        print "ball intersection with body: " , y
                        print "\n"
                        return True
        return False
        """





        """
        ERROR_VAL = 0.1 # acceptable change that doesn't trigger an update
        dist, bearing = self.dist, self.bearing
        last_dist, last_bearing = self.last_dist, self.last_bearing
        x1 = dist * cos(bearing)
        y1 = dist * sin(bearing)
        x2 = last_dist * cos(last_bearing)
        y2 = last_dist * sin(last_bearing)
        if self.DEBUG_INTERSECTION:
            print "\n"
            print "------------------------------------------------"
            print "x1=", x1, "  x2=", x2, "  y1=", y1, "  y2=", y2
            print "bearing=" ,bearing,"  dist=",dist
            print "last_bearing=", last_bearing, "  last_dist=", last_dist
            print "------------------------------------------------"
            print "\n"
        if (fabs(x1 - x2) > ERROR_VAL and fabs(y1 - y2) > ERROR_VAL):
            m = (y1 - y2) / (x1 - x2)
            if isX :
                x = (-y1 + m * x1) / m
                self.body_isect = x
                return True
            elif  x1 < x2 :#and fabs(y1-y2) < 1.5:
                y = y1 - m * x1
                self.body_isect = y
                print "ball intersection with body: " , y
                print "History" , self.history
                return True
            #theta=atan(m)
        return False
        """

    def calc_events(self, events, deferreds):
        """ get new values from proxy, return set of events """
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?
        (new_bearing, new_centerX, new_centerY, new_confidence,
                new_dist, new_elevation, new_focDist, new_height,
                    new_width) = ball_state = self._world.getVars(self._ball_vars)
        # getVars returns 'None' for non existant values. - TODO: check once on startup, not every iteration
        # calculate events.
        new_seen = (isinstance(new_dist, float) and new_dist > 0.0)
        if new_seen:
            self.missingFramesCounter = 0
            # convert degrees to radians
            new_bearing *= DEG_TO_RAD
            new_elevation *= DEG_TO_RAD
            # add event
            events.add(EVENT_BALL_IN_FRAME)
            self.update_location_body_coordinates(new_dist, new_bearing, new_elevation)
            self.compute_location_from_vision(new_centerX, new_centerY, new_width, new_height)
            if self.compute_intersection_with_body():
                events.add(EVENT_BALL_BODY_INTERSECT_UPDATE)
            #print "distance: man = %s, computed = %s" % (new_dist,
            #    getObjectDistanceFromHeight(max(new_height, new_width), self._real_length))
        else:
            # only update new_seen with a False value when some minimal "missing" frame counter is reach
            self.missingFramesCounter += 1
            if self.missingFramesCounter < MISSING_FRAMES_MINIMUM:
                new_seen = True
            
        if self.seen and not new_seen:
            events.add(EVENT_BALL_LOST)
        if not self.seen and new_seen:
            events.add(EVENT_BALL_SEEN)
        # TODO: we should only look at the localization supplied ball position,
        # and not the position in frame (image coordinates) or the relative position,
        # which may change while the ball is static.
        if new_seen and (abs(self.bearing - new_bearing) > MIN_BEARING_CHANGE or
                abs(self.dist - new_dist) > MIN_DIST_CHANGE):
            events.add(EVENT_BALL_POSITION_CHANGED)
        # store new values
        (self.centerX, self.centerY, self.confidence,
                self.elevation, self.focDist, self.height,
                    self.width) = (new_centerX, new_centerY, new_confidence, 
                        new_elevation, new_focDist, new_height, new_width)
        self.seen = new_seen
        
# TODO - CrossBar
# extra vars compared to GoalPost:
# 'LeftOpening', 'RightOpening', 'shotAvailable'
#self.shotAvailable = 0.0
#self.leftOpening = 0.0
#self.rightOpening = 0.0

class GoalPost(Locatable):

    def __init__(self, world, name, position_changed_event):
        super(GoalPost, self).__init__(world,
            real_length=GOAL_POST_DIAMETER)
        self._name = name
        self._position_changed_event = position_changed_event
        template = '/BURST/Vision/%s/%%s' % name
        self._vars = [template % s for s in ['AngleXDeg', 'AngleYDeg',
            'BearingDeg', 'CenterX', 'CenterY', 'Distance', 'ElevationDeg',
         'FocDist', 'Height', 'Width', 'X', 'Y']]
        self._world.addMemoryVars(self._vars)

        self.angleX = 0.0
        self.angleY = 0.0
        self.centerX = 0.0
        self.centerY = 0.0
        self.focDist = 0.0
        self.height = 0.0
        self.width = 0.0
        self.x = 0.0
        self.y = 0.0

    def calc_events(self, events, deferreds):
        """ get new values from proxy, return set of events """
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?
        (new_angleX, new_angleY, new_bearing, new_centerX, new_centerY,
                new_dist, new_elevation, new_focDist, new_height,
                new_width, new_x, new_y, 
                ) = new_state = self._world.getVars(self._vars)
        # calculate events
        new_seen = (isinstance(new_dist, float) and new_dist > 0.0)
        if new_seen: # otherwise new_elevation is 'None'
            self.missingFramesCounter = 0
            # convert to radians
            new_bearing *= DEG_TO_RAD
            if isinstance(new_elevation, float):
                new_elevation *= DEG_TO_RAD
            else:
                #print "%s - new_elevation == %r" % (self.__class__.__name__, new_elevation)
                pass
        else:
            # only update new_seen with a False value when some minimal "missing" frame counter is reach
            self.missingFramesCounter += 1
            if self.missingFramesCounter < MISSING_FRAMES_MINIMUM:
                new_seen = True
            
        # TODO: we should only look at the localization supplied ball position,
        # and not the position in frame (image coordinates) or the relative position,
        # which may change while the ball is static.
        if new_seen and (abs(self.bearing - new_bearing) > MIN_BEARING_CHANGE or
                abs(self.dist - new_dist) > MIN_DIST_CHANGE):
            self.update_location_body_coordinates(new_dist, new_bearing, new_elevation)
            events.add(self._position_changed_event)
        # store new values
        (self.angleX, self.angleY, self.centerX, self.centerY,
                self.focDist, self.height, self.width,
                self.x, self.y) = (
                  new_angleX, new_angleY, new_centerX,
                  new_centerY, new_focDist, new_height, new_width,
                  new_x, new_y)
        self.seen = new_seen
        
