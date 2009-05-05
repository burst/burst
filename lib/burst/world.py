from math import cos, sin, sqrt, pi, fabs
from time import time

import burst
from events import *

MIN_BEARING_CHANGE = 1e-3 # TODO - ?
MIN_DIST_CHANGE = 1e-3

DEG_TO_RAD = pi / 180.0

class Locatable(object):
    """ stupid name. It is short for "something that can be seen, holds a position,
    has a limited velocity which can be estimated, and is also interesting to the
    soccer game"

    Because of the way the vision system we use (northern's) works, we keep things
    in polar coordinates - bearing in radians, distance in centimeters.
    """

    REPORT_JUMP_ERRORS = True

    def __init__(self, memory, motion):
        self._memory = memory
        self._motion = motion
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

    def compute_location_from_vision(self, vision_x, vision_y):
        mat = self._motion.getForwardTransform('Head', 0) # TODO - can compute this here too. we already get the joints data. also, is there a way to join a number of soap requests together? (reduce latency for debugging)
        raise NotImplementedError('compute_location_from_vision')

    def update_location_body_coordinates(self, new_dist, new_bearing, new_elevation):
        """ We only update the values if the move looks plausible.
        
        TODO: This is a first order computation of velocity and position,
        removing outright outliers only. To be upgraded to a real localization
        system (i.e. reuse northern's code as a module, export variables).
        """
        newness = time()
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
        self.elevation = new_elevation
        self.newness = newness
        self.body_x, self.body_y = body_x, body_y
        self.vx, self.vy = dx/dt, dy/dt

class Movable(Locatable):
    def __init__(self, memory, motion):
        super(Movable, self).__init__(memory, motion)

class Ball(Movable):
    
    _name = 'Ball'

    DEBUG_INTERSECTION = False

    def __init__(self, memory, motion):
        super(Ball, self).__init__(memory, motion)
        self._ball_vars = ['/BURST/Vision/Ball/%s' % s for s in "bearing centerX centerY confidence dist elevation focDist height width".split()]

        self.centerX = 0.0
        self.centerY = 0.0
        self.confidence = 0.0
        self.focDist = 0.0
        self.height = 0.0
        self.width = 0.0
        self.seen = False

    def compute_intersection_with_body_x(self):
        ERROR_VAL = 0.1 # acceptable change that doesn't trigger an update
        dist, bearing = self.dist, self.bearing
        last_dist, last_bearing = self.last_dist, self.last_bearing
        x1 = dist * cos(bearing)
        y1 = dist * sin(bearing)
        x2 = last_dist * cos(last_bearing)
        y2 = last_dist * sin(last_bearing)
        if self.DEBUG_INTERSECTION:
            print "------------------------------------------------"
            print "x1=", x1, "  x2=", x2, "  y1=", y1, "  y2=", y2
            print "bearing=" ,bearing,"  dist=",dist
            print "last_bearing=", last_bearing, "  last_dist=", last_dist
            print "------------------------------------------------"
        if (fabs(x1 - x2) > ERROR_VAL and fabs(y1 - y2) > ERROR_VAL
            and y2 < y1 and dist < last_dist):
            m = (y1 - y2) / (x1 - x2)
            x = (-y1 + m * x1) / m
            self.body_x_isect = x
            #theta=atan(m)
            print "INFO: ball intersection with body x: %s" % x
            return True
        return False

    def calc_events(self):
        """ get new values from proxy, return set of events """
        events = set()
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?
        (new_bearing, new_centerX, new_centerY, new_confidence,
                new_dist, new_elevation, new_focDist, new_height,
                    new_width) = ball_state = self._memory.getListData(self._ball_vars)
        # getListData returns 'None' for non existant values. - TODO: check once on startup, not every iteration
        # calculate events.
        new_seen = (isinstance(new_dist, float) and new_dist > 0.0)
        if new_seen:
            # convert degrees to radians
            new_bearing *= DEG_TO_RAD
            new_elevation *= DEG_TO_RAD
            # add event
            events.add(EVENT_BALL_IN_FRAME)
            self.update_location_body_coordinates(new_dist, new_bearing, new_elevation)
            if self.compute_intersection_with_body_x():
                events.add(EVENT_BALL_BODY_X_ISECT_UPDATE)
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
        return events

class Robot(Movable):
    _name = 'Robot'

    def __init__(self, memory, motion):
        super(Robot, self).__init__(memory, motion)
        self._memory = memory
        self._motion = motion
        self.isWalkingActive = False
        self.isTurningActive = False
        self.walkID = 0
        self.turnID = 0
        
    def calc_events(self):
        """ get new values from proxy, return set of events """
        events = set()
        if self.isWalkingActive and not self._motion.isRunning(self.walkID): #self._motion.getRemainingFootStepCount() == 0 doesn't work in webots
            self.isWalkingActive = False
            events.add(EVENT_WALK_DONE)
        if self.isTurningActive and not self._motion.isRunning(self.turnID):
            self.isTurningActive = False
            events.add(EVENT_TURN_DONE)
        return events
        

class GoalPost(Locatable):

    def __init__(self, memory, motion, name, position_changed_event):
        super(GoalPost, self).__init__(memory, motion)
        self._name = name
        self._position_changed_event = position_changed_event
        template = '/BURST/Vision/%s/%%s' % name
        self._vars = [template % s for s in ['AngleXDeg', 'AngleYDeg',
            'BearingDeg', 'CenterX', 'CenterY', 'Distance', 'ElevationDeg',
         'FocDist', 'Height', 'LeftOpening', 'RightOpening', 'Width', 'X', 'Y',
         'shotAvailable']]

        self.angleX = 0.0
        self.angleY = 0.0
        self.centerX = 0.0
        self.centerY = 0.0
        self.focDist = 0.0
        self.height = 0.0
        self.leftOpening = 0.0
        self.rightOpening = 0.0
        self.width = 0.0
        self.x = 0.0
        self.y = 0.0
        self.shotAvailable = 0.0
        self.seen = False

    def calc_events(self):
        """ get new values from proxy, return set of events """
        events = set()
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?
        (new_angleX, new_angleY, new_bearing, new_centerX, new_centerY,
                new_dist, new_elevation, new_focDist, new_height,
                new_leftOpening, new_rightOpening, new_x, new_y, new_shotAvailable,
                    new_width) = new_state = self._memory.getListData(self._vars)
        # calculate events
        new_seen = (isinstance(new_dist, float) and new_dist > 0.0)
        if new_seen: # otherwise new_elevation is 'None'
            # convert to radians
            new_bearing *= DEG_TO_RAD
            if isinstance(new_elevation, float):
                new_elevation *= DEG_TO_RAD
            else:
                #print "%s - new_elevation == %r" % (self.__class__.__name__, new_elevation)
                pass
        # TODO: we should only look at the localization supplied ball position,
        # and not the position in frame (image coordinates) or the relative position,
        # which may change while the ball is static.
        if new_seen and (abs(self.bearing - new_bearing) > MIN_BEARING_CHANGE or
                abs(self.dist - new_dist) > MIN_DIST_CHANGE):
            self.update_location_body_coordinates(new_dist, new_bearing, new_elevation)
            events.add(self._position_changed_event)
        # store new values
        (self.angleX, self.angleY, self.centerX, self.centerY,
                self.focDist, self.height, self.leftOpening, self.rightOpening,
                self.x, self.y, self.shotAvailable, self.width) = (
                  new_angleX, new_angleY, new_centerX,
                  new_centerY, new_focDist, new_height,
                  new_leftOpening, new_rightOpening, new_x, new_y,
                  new_shotAvailable, new_width)
        self.seen = new_seen
        return events

BLUE_GOAL, YELLOW_GOAL = 1, 2

class Team(object):
    def __init__(self, world):
        # TODO: team info such as which team we are on, etc., is gotten from the game
        # controller, which we are currently missing.
        self._world = world
        self.setupBlueTeam()

    def setupBlueTeam(self):
        self.target_goal = YELLOW_GOAL
        self.our_goal = (self.target_goal is BLUE_GOAL and YELLOW_GOAL) or BLUE_GOAL
        # this is the event we check in order to calculate stuff
        self.target_goal_seen_event = EVENT_ALL_YELLOW_GOAL_SEEN
        self.left_post, self.right_post = self._world.yglp, self._world.ygrp

class Computed(object):
    """ place holder for any computed value, currently just the kicking point, that
    doesn't naturally belong to any other object, like ball speed etc
    """

    DEBUG_KP = False

    def __init__(self, world):
        self._world = world
        self._team = world.team
        # Kick Point
        self.kp = None
        self.kp_valid = False
        self.kp_k = 30.0

    def calc_events(self):
        """
        we calculate:
          kick point
        """
        events = set()
        if (self._team.target_goal_seen_event in self._world._events
            and EVENT_BALL_IN_FRAME in self._world._events):
            new_kp = self.calculate_kp()
            if not self.kp_valid or (new_kp[0] - self.kp[0] > 1e-5 or new_kp[1] - self.kp[1] > 1e-5):
                events.add(EVENT_KP_CHANGED)
            self.kp_valid = True
            self.kp = new_kp
        else:
            # cache the kp value it self until a new one comes
            self.kp_valid = False
        return events

    def calculate_kp(self):
        """ Our kicking point, first iteration, is a point k distant from the ball
        along the line connecting the point in the middle of the target goal
        and the ball in the outward direction.

        The coordinate system is not standard: the x axis is to the right of the robot,
        the y axis is to the front. The bearing is measured from the y axis ccw.
        """
        # left - l, right - r, bearing - b, dist - d
        team = self._team
        left_post, right_post, ball = team.left_post, team.right_post, self._world.ball
        lb, ld, rb, rd = (left_post.bearing, left_post.dist,
                right_post.bearing, right_post.dist)
        bb, bd = ball.bearing, ball.dist
        bx, by = bd * sin(bb), bd * cos(bd)
        k = self.kp_k
        cx = (rd * sin(rb) + ld * sin(lb)) / 2.0
        cy = (rd * cos(rb) + ld * cos(lb)) / 2.0
        nx, ny = bx - cx, by - cy
        nnorm = sqrt(nx**2 + ny**2)
        nx, ny = nx / nnorm, ny / nnorm
        kpx, kpy = bx + k * nx, by + k * ny
        if self.DEBUG_KP:
            print "KP: b (%3.3f, %3.3f), c(%3.3f, %3.3f), n(%3.3f, %3.3f), kp(%3.3f, %3.3f)" % (bx, by, cx, cy, nx, ny, kpx, kpy)
        return kpx, kpy

class World(object):

    def __init__(self):
        self._memory = burst.getMemoryProxy()
        self._motion = burst.getMotionProxy()
        self._events = set()

        # Stuff that we prefer the users use directly doesn't get a leading underscore
        self.ball = Ball(self._memory, self._motion)
        self.bglp = GoalPost(self._memory, self._motion, 'BGLP', EVENT_BGLP_POSITION_CHANGED)
        self.bgrp = GoalPost(self._memory, self._motion, 'BGRP', EVENT_BGRP_POSITION_CHANGED)
        self.yglp = GoalPost(self._memory, self._motion, 'YGLP', EVENT_YGLP_POSITION_CHANGED)
        self.ygrp = GoalPost(self._memory, self._motion, 'YGRP', EVENT_YGRP_POSITION_CHANGED)
        self.robot = Robot(self._memory, self._motion)
        # construct team after all the posts are constructed, it keeps a reference to them.
        self.team = Team(self)
        self.computed = Computed(self)

        # all objects that we delegate the event computation and naoqi interaction to.
        # TODO: we have the exact state of B-HUMAN, so we could use exactly their solution,
        # and hence this todo. We have multiple objects that calculate their events
        # based on ground truths (naoqi proxies) and on calculated truths. We need to
        # rerun them every time something is updated, *in the correct order*. So right
        # now I'm hardcoding this by using an ordered list of lists, but later this
        # should be calculated by storing a "needed" and "provided" list, just like B-HUMAN,
        # and doing the sorting once (and that value can be cached to avoid recomputing on
        # each run).
        self._objects = [
            # All basic objects that rely on just naoproxies should be in the first list
            [self.ball, self.bglp, self.bgrp, self.yglp, self.ygrp, self.robot],
            # anything that relies on basics but nothing else should go next
            [self],
            # self.computed should always be last
            [self.computed],
        ]

    def calc_events(self):
        """ World treats itself as a regular object by having an update function,
        this is called after the basic objects and before the computed object (it
        may set some events / variables needed by the computed object)
        """
        events = set()
        if self.bglp.seen and self.bgrp.seen:
            events.add(EVENT_ALL_BLUE_GOAL_SEEN)
        if self.yglp.seen and self.ygrp.seen:
            events.add(EVENT_ALL_YELLOW_GOAL_SEEN)
        return events

    def update(self):
        # TODO: automatic calculation of event dependencies (see constructor)
        for objlist in self._objects:
            for obj in objlist:
                self._events.update(obj.calc_events())

    def getEvents(self):
        events = self._events
        self._events = set()
        return events

