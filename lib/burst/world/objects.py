from math import cos, sin, sqrt, pi, fabs, atan, atan2
from textwrap import wrap
import logging

from burst_util import nicefloat, nicebool
from burst_consts import (BALL_REAL_DIAMETER, DEG_TO_RAD,
    MISSING_FRAMES_MINIMUM, MIN_BEARING_CHANGE,
    MIN_DIST_CHANGE, GOAL_POST_DIAMETER,
    DEFAULT_NORMALIZED_CENTERING_X_ERROR, DEFAULT_NORMALIZED_CENTERING_Y_ERROR,
    CONSOLE_LINE_LENGTH, CENTERING_MINIMUM_PITCH, ID_NOT_SURE, ID_SURE,
    IMAGE_CENTER_X, IMAGE_CENTER_Y, PIX_TO_RAD_X, PIX_TO_RAD_Y,
    YELLOW_GOAL)
import burst_consts
from burst_events import (EVENT_BALL_IN_FRAME,
    EVENT_BALL_BODY_INTERSECT_UPDATE, EVENT_BALL_LOST,
    EVENT_BALL_SEEN, EVENT_BALL_POSITION_CHANGED , BALL_MOVING_PENALTY,
    event_name, FIRST_EVENT_NUM)
from burst_util import running_median, RingBuffer, Nameable, func_name, gettb
from burst.image import normalized2_image_width, normalized2_image_height
import burst
import burst_events
import burst.field as field

################################################################################

logger = logging.getLogger('objects')
info = logger.info

################################################################################

def once_per_step(f):
    def wrapper(self, *args, **kw):
        if hasattr(self, '_once_per_step_time') and self._world.time == self._once_per_step_time:
            print "ERROR: called twice per round: %s" % func_name(f)
            import pdb; pdb.set_trace()
            return
        self._once_per_step_time = self._world.time
        self._last_tb = gettb()
        return f(self, *args, **kw)
    return wrapper

class CenteredLocatable(object):
    """ store data for a Locatable for a current search.
    Stored inside the Locatable itself for usage by Localization.
    Updated by Searcher using Tracker (in actions.headtracker).
    """

    def __init__(self, target):
        """ target - Locatable to keep track of.
        """
        self._target = target
        self._world = target._world
        self.clear()

    def clear(self):
        # 3d based estimates
        self.elevation, self.dist, self.bearing = 0.0, 0.0, 0.0
        # image based
        self.centerX, self.centerY = 0.0, 0.0
        self.normalized2_centerX, self.normalized2_centerY = 0.0, 0.0
        # body angles (body space?)
        self.head_yaw, self.head_pitch = 0.0, 0.0
        self.sighted = False
        self.sighted_centered = False # is True if last sighting was centered
        self.update_time = -1000.0

    def get_yaw_pitch(self):
        return self.head_yaw, self.head_pitch
    yaw_pitch = property(get_yaw_pitch)

    def __str__(self):
        #return '\n'.join(wrap('{%s}' % (', '.join(('%s:%s' % (k, nicefloat(v))) for k, v in self.__dict__.items() )), CONSOLE_LINE_LENGTH))
        return '%s %s %3.2f %3.2f' % (nicebool(self.sighted), nicebool(self.sighted_centered),
            self.head_yaw, self.head_pitch)

    def _update(self):
        """ Update for self._target. Only stores the
        results for the most centered sighting - this includes
        everything, vision (centerX/centerY), joint angles (headYaw, headPitch),
        and the world location estimates (distance, bearing, elevation)
        """
        # TODO - if we saw everything then stop scan
        # TODO - if we saw something then track it, only then continue scan
        target = self._target
        if not target.seen: return

        if self.sighted: # always do first update
            # We keep the most centered head_yaw and head_pitch using smallest norm2.
            abs_cur_x, abs_cur_y = abs(self.normalized2_centerX), abs(self.normalized2_centerY)
            abs_new_x, abs_new_y = abs(target.normalized2_centerX), abs(target.normalized2_centerY)
            new_dist = abs_new_x**2 + abs_new_y**2
            old_dist = abs_cur_x**2 + abs_cur_y**2
            if new_dist >= old_dist:
                return # no update

        if burst.options.verbose_localization:
            print "Locatable (Searcher): updating %s, (%1.2f, %1.2f) -> (%1.2f, %1.2f)" % (
                target.name,
                self.normalized2_centerX or -100.0, self.normalized2_centerY or -100.0,
                target.normalized2_centerX, target.normalized2_centerY)

        if hasattr(target, 'distSmoothed'):
            self.distSmoothed = target.distSmoothed
        # relative location from naoman
        self.dist = target.dist # TODO - dist->distance
        self.bearing = target.bearing
        self.elevation = target.elevation
        self.head_yaw = self._world.getAngle('HeadYaw')
        self.head_pitch = self._world.getAngle('HeadPitch')
        # vision vars from naoman
        self.height = target.height
        self.width = target.width
        self.centerX = target.centerX
        self.centerY = target.centerY
        self.normalized2_centerX = target.normalized2_centerX
        self.normalized2_centerY = target.normalized2_centerY
        self.x = target.x # upper left corner - not valid for Ball
        self.y = target.y #
        # flag the sighted flag
        self.sighted = True
        # TODO - all of these centered flags are very confused - bad naming, not
        # clear who computed what, multiple ways to compute same thing (is Ball centered)
        self.sighted_centered = target.centered or target.centered_at_pitch_limit
        self.update_time = self._world.time

    def estimated_yaw_and_pitch_to_center(self):
        """ return yaw and pitch that should bring this object into the center of
        the image """
#        if self.centerX == None or self.centerY == None:
#            import pdb; pdb.set_trace()
        try:
            float(self.centerX)
        except:
            import pdb; pdb.set_trace()
        delta_yaw   = - PIX_TO_RAD_X * (self.centerX - IMAGE_CENTER_X)
        delta_pitch =   PIX_TO_RAD_Y * (self.centerY - IMAGE_CENTER_Y)
        yaw = self.head_yaw + delta_yaw
        pitch = self.head_pitch + delta_pitch
        #self._report("centering initial move towards %s, %1.2f+%1.2f, %1.2f+%1.2f" % (
        #    target.name, target.centered_self.head_yaw, delta_yaw,
        #    target.centered_self.head_pitch, delta_pitch))
        return yaw, pitch


class Locatable(Nameable):
    """ stupid name. It is short for "something that can be seen, holds a position,
    has a limited velocity which can be estimated, and is also interesting to the
    soccer game"

    Because of the way the vision system we use (northern's) works, we keep things
    in polar coordinates - bearing in radians, distance in centimeters.
    """

    REPORT_JUMP_ERRORS = False
    HISTORY_SIZE = 20

    def __init__(self, name, world, real_length, world_x=None, world_y=None):
        """
        real_length - [cm] real world largest diameter of object.
        memory, motion - proxies to ALMemory and ALMotion respectively.
        world_x, world_y - [cm] locations in world coordinate frame. World
        coordinate frame (reminder) origin is in our team goal center, x
        axis is towards opposite goal, y axis is to the left (complete a right
        handed coordinate system).
        """
        super(Locatable, self).__init__(name)
        self._world = world
        # cached proxies
        self._memory = world._memory
        self._motion = world._motion
        # longest arc across the object, i.e. a diagonal.
        self._real_length = real_length

        # This is the world x coordinate. Our x axis is to the right of our goal
        # center, and our y is towards the enemy gate^H^H^Hoal. The enemy goal is up.
        # (screw Ender)

        # default to estimating everything is in center of field.
        self.world_x = world_x if world_x is not None else field.MIDFIELD_X
        self.world_y = world_y if world_y is not None else field.MIDFIELD_Y # TODO - is't wise?
        self.world_heading = 0.0 # default to pointing towards target goal

        self.history = RingBuffer(Locatable.HISTORY_SIZE) # stores history for last

        # This is the player body frame relative bearing. radians.
        self.bearing = 0.0
        self.elevation = 0.0
        # This is the player body frame relative distance. centimeters.
        self.dist = 0.0
        self.update_time = 0.0 # time of current update
        # previous non zero values
        self.last_bearing = 0.0
        self.last_dist = 0.0
        self.last_elevation = 0.0
        self.last_update_time = 0.0 # time of previous update
        # Body coordinate system: x is to the right (body is the torso, and generally
        # the forward walk direction is along the y axis).
        self.body_x = 0.0
        self.body_y = 0.0

        # upper barrier on speed, used to remove outliers. cm/sec
        self.upper_v_limit = 400.0

        self.seen = False
        self.recently_seen = False          # Was the object seen within MISSING_FRAMES_MINIMUM
        self.centered = False               # whether the distance from the center is smaller then XXX
        self.centered_at_pitch_limit = False # centered on X axis, on pitch low limit (looking most upwardly)
        self.missingFramesCounter = MISSING_FRAMES_MINIMUM # start as "not seen for inifinity". This is close enough.

        # smoothed variables
        self.distSmoothed = 0.0
        self.distRunningMedian = running_median(3) # TODO: Change to ballEKF/ballLoc?
        self.distRunningMedian.next()

        # Vision variables defaults
        self.centerX = None
        self.centerY = None
        self.normalized2_centerX = None
        self.normalized2_centerY = None
        self.x = None
        self.y = None

        # centered - a copy of some of the values that keeps
        # the current searcher values for this target.
        self.centered_self = CenteredLocatable(self)

    def get_xy(self):
        return self.world_x, self.world_y

    xy = property(get_xy)

    def centering_error(self, normalized_error_x=DEFAULT_NORMALIZED_CENTERING_X_ERROR,
            normalized_error_y=DEFAULT_NORMALIZED_CENTERING_Y_ERROR):
        """ calculate normalized error from image center for object, using
        centerX and centerY from vision, using given defaults for what "centered"
        means (i.e. what the margins are).

        Return: centered, x_normalized_error, y_normalized_error
         errors are in [-1, 1]
        """
        # TODO - using target.centerX and target.centerY without looking at update_time is broken.
        # Normalize ball X between 1 (left) to -1 (right)
        assert(normalized_error_x > 0 and normalized_error_y > 0)
        xNormalized = normalized2_image_width(self.centerX)
        # Normalize ball Y between 1 (top) to -1 (bottom)
        yNormalized = normalized2_image_height(self.centerY)

        cur_pitch = self._world.getAngle('HeadPitch')
        pitch_barrier = CENTERING_MINIMUM_PITCH
        elevation_on_upper_edge = cur_pitch < pitch_barrier
        centered_at_pitch_limit = (elevation_on_upper_edge and yNormalized < 0 and
            abs(xNormalized) < normalized_error_x)
        centered = (abs(xNormalized) <= normalized_error_x and
                abs(yNormalized) <= normalized_error_y)

        return centered, centered_at_pitch_limit ,xNormalized, yNormalized

    def calc_recently_seen(self, new_seen):
        """ sometimes we don't want to know if the object is visible this frame,
        it is enough if it is visible for the last few frames
        """
        new_recently_seen = new_seen
        if new_seen: # otherwise new_elevation is 'None'
            self.missingFramesCounter = 0
        else:
            # only update new_seen with a False value when some minimal "missing" frame counter is reach
            self.missingFramesCounter += 1
            if self.missingFramesCounter < MISSING_FRAMES_MINIMUM:
                new_recently_seen = True
        return new_recently_seen

    # History related stuff

    HISTORY_LABELS = ['time', 'distance', 'bearing', 'head_yaw', 'head_pitch']
    HIST_TIME, HIST_DIST, HIST_BEARING, HIST_YAW, HIST_PITCH = range(5)
    def _record_current_state(self):
        """ pushes new values into the history buffer. called from
        update_location_body_coordinates
        """
        self.history.ring_append([self.update_time, self.dist, self.bearing,
            self.centered_self.head_yaw, self.centered_self.head_pitch])

    @property
    def seenWithinOneFrame(self):
        min_dt = 0.2 # TODO - constant this. Also - eventmanager dependency?
        return self.seen or (
             self._world.time - self.history[-1][self.HIST_TIME] <= min_dt if self.history[-1] else False)

    @once_per_step
    def update_location_body_coordinates(self, new_dist, new_bearing, new_elevation):
        """ We only update the values if the move looks plausible.

        TODO: This is a first order computation of velocity and position,
        removing outright outliers only. To be upgraded to a real localization
        system (i.e. reuse northern's code as a module, export variables).
        """
        update_time = self._world.time
        dt = update_time - self.update_time
        if dt <= 0.0:
            print "TIME ERROR: dt = %s, not updating anything" % dt
            import pdb; pdb.set_trace()
            return
        body_x, body_y = new_dist * cos(new_bearing), new_dist * sin(new_bearing)
        dx, dy = body_x - self.body_x, body_y - self.body_y
        if dx**2 + dy**2 > (dt * self.upper_v_limit)**2:
            # no way this body jumped that quickly
            if self.REPORT_JUMP_ERRORS:
                print "JUMP ERROR: %s:%s - %s, %s -> %s, %s - bad new position value, not updating" % (
                    self.__class__.__name__, self.name, self.body_x, self.body_y, body_x, body_y)
            return

        self.last_update_time, self.last_dist, self.last_elevation, self.last_bearing = (
            self.update_time, self.dist, self.elevation, self.bearing)

        self.bearing = new_bearing
        self.dist = new_dist
        self._record_current_state()
        self.distSmoothed = self.distRunningMedian.send(new_dist)
        #if isinstance(self, Ball):
        #    print "%s: self.dist, self.distSmoothed: %3.3f %3.3f" % (self, self.dist, self.distSmoothed)

        self.elevation = new_elevation
        self.update_time = update_time
        self.body_x, self.body_y = body_x, body_y
        self.vx, self.vy = dx/dt, dy/dt

    def update_centered(self):
        """ call this after all vision variables have been updated. It computes
        the centering error (distance from center along both axis normalized to
        [-1, 1]) and stores in self.centered_self the most centered sighting with
        all parameters including body angles. """
        (self.centered,
         self.centered_at_pitch_limit,
         self.normalized2_centerX,
         self.normalized2_centerY,
            ) = self.centering_error()

        if burst.options.debug:
            print "%s: update_centered: %s %1.2f %1.2f" % (self.name,
                self.centered, self.normalized2_centerX, self.normalized2_centerY)

        self.centered_self._update() # must be after updating self.normalized2_center{X,Y}

    def __str__(self):
        return "<%s; (%3.2f,%3.2f,%3.2f,%3.2f), cl=%s>" % (self.name, self.update_time, self.dist, self.bearing, self.elevation, str(self.centered_self))

class Movable(Locatable):
    def __init__(self, name, world, real_length):
        super(Movable, self).__init__(name, world, real_length)

class Ball(Movable):

    in_frame_event = EVENT_BALL_IN_FRAME
    lost_event = EVENT_BALL_LOST

    DEBUG_INTERSECTION = False

    def __init__(self, world):
        super(Ball, self).__init__('Ball', world,
            real_length=BALL_REAL_DIAMETER)
        self._ball_vars = ['/BURST/Vision/Ball/%s' % s for s in "BearingDeg CenterX CenterY Confidence Distance ElevationDeg FocDist Height Width".split()]
        self._world.addMemoryVars(self._ball_vars)

        self.centerX = 0.0
        self.centerY = 0.0
        self.confidence = 0.0
        self.focDist = 0.0
        self.height = 0.0
        self.width = 0.0
        self.body_isect = None
        self.base_point = None
        self.base_point_index = 0
        self.avrYplace = None
        self.avrYplace_index = 0
        self.sumY = 0
        self.dy = 0
        self.velocity = None
        self.time_intersection = None
        self.shouldComputeIntersection = False

    #for robot body when facing the other goal
    def compute_intersection_with_body(self):

        if not self.shouldComputeIntersection:
            return False

        T = 0
        DIST = 1
        BEARING = 2

        X = 1
        Y = 2

        ERROR_VAL_X = 10
        ERROR_VAL_Y = 0
        NUM_OF_POINTS = 10

        if not self.CalcIsBallMoving():
            return False

        if self.history[0] != None:
            if self.base_point_index == 0:
                self.base_point = [self.history[0][T] , self.history[0][DIST] * cos(self.history[0][BEARING]) \
                                   , self.history[0][DIST] * sin(self.history[0][BEARING])]
        else:
            return False

        #vars for least mean squares
        self.base_point_index = 1
        last_point = self.base_point
        sumX = last_point[X]
        sumXY = last_point[X] * last_point[Y]
        sumY = last_point[Y]
        sumSqrX =  last_point[X] * last_point[X]
        sumT = 0 # T0= 0
        sumXT = last_point[X] * 0 # T0= 0
        sumSqrT = 0 * 0 # T0= 0

        n = 1
        for point in self.history:
            if point != None:
                if n == 1:
                    n += 1
                    continue #first point was calc already
                if n <= self.base_point_index:
                    n += 1
                    continue #skipping nonrelvant point
                cor_point = [point[T] , point[DIST] * cos(point[BEARING]) , point[DIST] * sin(point[BEARING])]
#                if cor_point[X] > (last_point[X] + ERROR_VAL_X): #checking if not moving toward our goalie
#                    self.base_point = cor_point
#                    if self.history[0] != None:
#                        self.base_point_index = n -1
#                    else:
#                        self.base_point_index = n
#                    return False
                sumX += cor_point[X]
                sumXY += cor_point[X] * cor_point[Y]
                sumY += cor_point[Y]
                sumSqrX +=  cor_point[X] * cor_point[X]
                sumT += cor_point[T] - last_point[T]
                sumXT += cor_point[X] * (cor_point[T] - last_point[T])
                sumSqrT += (cor_point[T] - last_point[T]) * (cor_point[T] - last_point[T])

                last_point = cor_point
                n += 1
            else:
                if n < NUM_OF_POINTS: #TODO: need some kind of col' for diffrent speeds....
                    return False
                break

        n = n - self.base_point_index #real number of valid points


        if n >= NUM_OF_POINTS:#TODO: need some kind of col' for diffrent speeds....
            #Least mean squares (http://en.wikipedia.org/wiki/Linear_least_squares):
            if fabs((sumX * sumX) - (n * sumSqrX))  >  ERROR_VAL_X:
                self.body_isect = ((sumX * sumXY) - (sumY * sumSqrX)) / ((sumX * sumX) - (n * sumSqrX))
                slop = ((sumY * sumX) - (n * sumXY)) / ((sumX * sumX) - (n * sumSqrX))


                #calc time for intersection:
                #finding the x coordinate of two point on the regression line
                if slop != 0:
                    slop2 = -1/slop
                    n_last_point = last_point[Y] - slop2 * last_point [X]
                    n_base_point = self.base_point[Y] - slop2 * self.base_point[X]
                    if (slop - slop2) != 0:
                        x_last_point = (n_last_point - self.body_isect) / (slop - slop2)
                        x_base_point = (n_base_point - self.body_isect) / (slop - slop2)
                        dx1 = x_last_point - x_base_point
                        dt1 = last_point [T] - self.base_point[T]
                        if dt1 != 0 and dx1 != 0:
                            self.velocity = dx1/dt1
                            dx2 = 0 - last_point[X]
                            self.time_intersection = dx2/self.velocity
                            #print "velocity: ", self.velocity
                            #print "time for intersection: ", self.time_intersection

                return True
        if self.history[0] != None:
            self.base_point_index -= 1
        return False


    def movingBallPenalty(self):

        ERROR_IN_Y = 2

        if self.avrYplace_index >= 20:
            self.dy = (self.dist * sin(self.bearing)) - self.avrYplace
            if fabs(self.dy) > ERROR_IN_Y:
                return True

        self.avrYplace_index += 1
        self.sumY += self.dist * sin(self.bearing)
        self.avrYplace = self.sumY / self.avrYplace_index

        return False

    def CalcIsBallMoving(self):

        #The error functions (for ball.dist):
        #10.33 < x < 120 : f = 0.2955 * x - 10.33
        #120 <= x : f = 0.00136 * x ^ 1.94609
        T = 0
        DIST = 1
        BEARING = 2

        ERROR_VAR = 1
        NUM_OF_CHANGED_POINTS = 5

        i = 0
        dist_list = []
        dist_list_sub = []
        for point in self.history:
            if point == None:
                break
            if len(dist_list) == 0:
                dist_list.append(point[DIST])
                continue
            if fabs(point[DIST] - dist_list[i]) > ERROR_VAR:
                i += 1
                dist_list.append(point[DIST])
                dist_list_sub.append(dist_list[i] - dist_list[i-1])

        if len(dist_list) < NUM_OF_CHANGED_POINTS:
            return False

        for i in range(1,NUM_OF_CHANGED_POINTS -1):
            if dist_list_sub[-i] > 0:
                return False

        #print "Ball comming"
        return True


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
            # convert degrees to radians
            new_bearing *= DEG_TO_RAD
            new_elevation *= DEG_TO_RAD
            # add event
            events.add(EVENT_BALL_IN_FRAME)
            self.update_location_body_coordinates(new_dist, new_bearing, new_elevation)
            if self.compute_intersection_with_body():
                events.add(EVENT_BALL_BODY_INTERSECT_UPDATE)
            if self.movingBallPenalty():
                self.avrYplace = None
                self.avrYplace_index = 0
                self.sumY = 0
                events.add(BALL_MOVING_PENALTY) # TODO - WTF is this name? does it mean the ball moved and caused a penalty?
            #print "distance: man = %s, computed = %s" % (new_dist,
            #    getObjectDistanceFromHeight(max(new_height, new_width), self._real_length))

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
        self.recently_seen = self.calc_recently_seen(new_seen)
        if self.seen:
            self.update_centered()

# TODO - CrossBar
# extra vars compared to GoalPost:
# 'LeftOpening', 'RightOpening', 'shotAvailable'
#self.shotAvailable = 0.0
#self.leftOpening = 0.0
#self.rightOpening = 0.0

class Goal(Locatable):
    """ The location of the goal is the location of the center of the goal.
    There is no visual object for Goal, but it is a useful abstraction since
    we aim to defend / score to this location.

    Also, since the vision code will tell us that the left post is the right
    post if it only sees the start of it, it is useful for the code to actually
    look at the goal and not at the post itself at times (i.e. the goal location will
    be relatively known while the left/right is not).

    This calc_events replaces the calc_events for the respective posts
    """

    def __init__(self, name, world, which_team, left_name, right_name, left_world, right_world):
        mid_x, mid_y = ((left_world[0]+right_world[0])/2.0,
                        (left_world[1]+right_world[1])/2)
        super(Goal, self).__init__(name, world,
            real_length=burst.field.CROSSBAR_CM_WIDTH, world_x=mid_x, world_y=mid_y)
        self.left = GoalPost(name=left_name, which_team=which_team, world=world, world_x=left_world[0],
                world_y=left_world[1])
        self.right = GoalPost(name=right_name, which_team=which_team, world=world, world_x=right_world[0],
                world_y=right_world[1])
        self.unknown = GoalPost(name='%s_UnknownPost' % name, which_team=which_team, world=world, world_x=mid_x,
                world_y=mid_y, real_post=False)
        self.bottom_top = (self.left, self.right) if self.left.world_y < self.right.world_y else (self.right, self.left)

    def configure(self, color):
        """ called when entering CONFIGURED state """
        for post in [self.left, self.right, self.unknown]:
            post.configure(color=color)
        # TODO - calculate the in_frame event for this goal

    def calc_events(self, events, deferreds):
        """ Try to get the location of the left/right posts from the unknown harder.
        """
        # First read vars and check
        if self.left.color is None: return
        self.left.get_new_state()
        self.right.get_new_state()
        left_seen_uncertain = self.left.is_uncertain()
        right_seen_uncertain = self.right.is_uncertain()
        to_second_stage = []
        # States:
        if left_seen_uncertain and right_seen_uncertain:
            # should never happen
            to_second_stage.append(self.unknown)
            state = self.left.get_state() if left_seen_uncertain else self.right.get_state()
            print "BOTH UNCERTAIN AND SEEN??"
            import pdb; pdb.set_trace()
            self.unknown.set_state(state)
        elif left_seen_uncertain or right_seen_uncertain:
            # one uncertain, the other maybe certain or not.
            # TODO: use the unknown to update the one the correct post.
            # right now: we just update the unknown.
            uncertain_one = self.left if left_seen_uncertain else self.right
            other = self.right if left_seen_uncertain else self.left
            self.unknown.set_state(uncertain_one.get_state())
            to_second_stage = [self.unknown, other]
        else:
            # none seen uncertain - either both seen, one seen or none, so let the standard update happen
            to_second_stage = [self.left, self.right]
            self.unknown.seen = False
        for obj in to_second_stage:
            obj.second_stage_calc_events(events, deferreds)
        self.seen = self.left.seen or self.right.seen or self.unknown.seen
        # TODO - thrown the team event here? instead of world.__init__

class GoalPost(Locatable):
    """ We turned things around - now the goal posts and the goals know if they
    are opposing or our from the start, they just don't know the color until configured.
    This means the eyes won't show the color right now until we are configured.
    """

    def __init__(self, name, which_team, world, world_x, world_y, real_post=True):
        """
        name - printable name
        which_team - 'Opposing' or 'Our' - used to deduce left or right (TODO - the
        situation of deduced and assumed information is convoluted).
        """
        super(GoalPost, self).__init__(name, world,
            real_length=GOAL_POST_DIAMETER, world_x=world_x, world_y=world_y)
        self.real_post = real_post
        self.which_team = which_team
        self.id_certainty = ID_NOT_SURE
        # Stuff that is defined only after Player.onConfigured is called:
        self.color = None
        self.in_frame_event = None
        self._vars = None

    @staticmethod
    def getVarsForName(name):
        template = '/BURST/Vision/%s/%%s' % name
        return [template % s for s in ['AngleXDeg', 'AngleYDeg',
            'BearingDeg', 'CenterX', 'CenterY', 'Distance', 'ElevationDeg',
         'FocDist', 'Height', 'Width', 'X', 'Y', 'IDCertainty']]

    def is_left(self):
        return ((self.world_y > 0 and self.which_team == field.OUR_TEAM)
                or (self.world_y < 0 and self.which_team == field.OPPOSING_TEAM))

    def fourLetterPostName(self):
        return '%sG%sP' % ('Y' if self.color == YELLOW_GOAL else 'B',
            'L' if self.is_left() else 'R')

    def configure(self, color):
        """ called from onConfigure """
        self.color = color
        event_data = burst_consts.goal_events[color]['left' if self.is_left() else 'right']
        self._position_changed_event = event_data['position_changed'] if self.real_post else -1
        self.in_frame_event = event_data['in_frame'] if self.real_post else -1
        self._vars = self.getVarsForName(self.fourLetterPostName())
        info('Configuring %s' % self.goalPostToString())

    def goalPostToString(self):
        return ('%(name)s %(color)s, %(which)s, (%(x)3.2f, %(y)3.2f), %(left)s, %(four)s' %
                dict(name=self.name,
                    color=self.color,
                    which=self.which_team,
                    x=self.world_x,
                    y=self.world_y,
                    left='left' if self.is_left() else 'right',
                    four=self.fourLetterPostName()))

    def get_new_state(self):
        # must be called first before calling anything else
        self._vars_values = self._world.getVars(self._vars)
        return self._vars_values

    def get_state(self):
        return self._vars_values

    def set_state(self, state):
        self._vars_values = state

    def is_uncertain(self):
        (new_angleX, new_angleY, new_bearing, new_centerX, new_centerY,
                new_dist, new_elevation, new_focDist, new_height,
                new_width, new_x, new_y, new_id_certainty
                ) = self._vars_values
        return new_id_certainty != ID_SURE and new_dist > 0.0

    def second_stage_calc_events(self, events, deferreds):
        """ get new values from proxy, return set of events """
        # TODO: this is ugly - there is an idiom of using a class as a list
        # and a 'struct' at the same time - somewhere in activestate.com?

        # If we are uncofigured we cannot update anything
        if self.color is None: return

        # calculate events
        (new_angleX, new_angleY, new_bearing, new_centerX, new_centerY,
                new_dist, new_elevation, new_focDist, new_height,
                new_width, new_x, new_y, new_id_certainty
                ) = self._vars_values

        new_seen = isinstance(new_dist, float) and new_dist > 0.0

        if new_seen:
            if events is not None and self.in_frame_event >= FIRST_EVENT_NUM:
                events.add(self.in_frame_event)
            # convert to radians
            new_bearing *= DEG_TO_RAD
            if isinstance(new_elevation, float):
                new_elevation *= DEG_TO_RAD

        # TODO: we should only look at the localization supplied ball position,
        # and not the position in frame (image coordinates) or the relative position,
        # which may change while the ball is static.
        if new_seen and (abs(self.bearing - new_bearing) > MIN_BEARING_CHANGE or
                abs(self.dist - new_dist) > MIN_DIST_CHANGE):
            self.update_location_body_coordinates(new_dist, new_bearing, new_elevation)
            if events is not None and self._position_changed_event >= FIRST_EVENT_NUM:
                events.add(self._position_changed_event)
        # store new values
        (self.angleX, self.angleY, self.centerX, self.centerY,
                self.focDist, self.height, self.width,
                self.x, self.y) = (
                  new_angleX, new_angleY, new_centerX,
                  new_centerY, new_focDist, new_height, new_width,
                  new_x, new_y)
        self.seen = new_seen
        self.recently_seen = self.calc_recently_seen(new_seen)
        if self.seen:
            self.update_centered()
            self.update_time = self._world.time

