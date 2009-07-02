"""
Localization object that belongs to world, and is called once
per step. In charge of updating various positions, world coordinates
and otherwise.
"""

from burst_util import nicefloat
from burst_consts import RAD_TO_DEG

import burst
from burst_events import EVENT_WORLD_LOCATION_UPDATED
from burst.field import (GOAL_POST_CM_HEIGHT, CROSSBAR_CM_WIDTH,
    CROSSBAR_CM_WIDTH, white_limits)
from burst.position import xyt_from_two_dist_one_angle
from math import asin

# TODO - utilize constants from central location in place of those
GOAL_SIZE = 150 #sizeof goal (cm)
FIELD_SIZE = 605 #sizeof field (cm)
HALF_GOAL_SIZE = (GOAL_SIZE/2)


class Localization(object):
    """ Names. This is the Localization object. It is responsible for computing the
    world position of the robot and anything else. It doesn't actually go and
    look for information. That is a Behavior thing, which the Localizer takes
    care of. """

    def __init__(self, world):
        self._world = world
        self._pose = world.pose
        # Location of robot (ourselves)
        self._location = None
        # Location of ball
        self._ball_location = None
        # store bottom and top posts
        self._bottom, self._top = self._world.opposing_goal.bottom_top
        # read verboseness flag at construction time
        self.verbose = burst.options.verbose_localization

        self._history = [] # (t, x, y, heading)

    def calc_events(self, events, deferreds):
        """
        Update position of robot based on newly centered goal posts.
        """
        # First, check for each of the goal posts, if it is visibile dead center, then
        # update it's location.
        # Second, if an update occured, and the other post is also updated without any
        # movement in between, update our location.
        # This, coupled with the localizer which initiates a search for both posts,
        # will ensure an update of the location.
        # Additionally, oppurtunistic updates will be possible (though not expected
        # until we add more landmarks like intersections etc.)
        # On the gripping hand, this is the perfect place to do Particle Filter / Kalman
        # Filter updates from landmarks, once such code exists.

        # We defer updating pose until we actually need it.
        new_dist = False
        bottom, top = self._bottom, self._top
        #if self.verbose:
        #    bottom_c, top_c = bottom.centered_self, top.centered_self
        #    if self.verbose and bottom.seen and top.seen:
        #        print "Localization: UPDATE DIST POSSIBLE? (%s, %s), (%s, %s)" % (
        #            bottom_c.normalized2_centerX, bottom_c.normalized2_centerY,
        #            top_c.normalized2_centerX, top_c.normalized2_centerY
        #        )

        # Also update the distance to the ball - not sure if it will be used, but not
        # bad as a test.
        ball = self._world.ball
        if ball.seen and ball.centered_at_pitch_limit or ball.centered:
            self.updatePoseAndCalcDistance(ball)
        for obj, other_obj in ((bottom, top), (top, bottom)):
            if obj.seen and obj.centered_at_pitch_limit or obj.centered:
                if self.verbose:
                    o_centered = other_obj.centered_self
                    other = (o_centered.sighted_centered and
                            ('was seen centered %3.2f seconds ago' % (self._world.time -
                                o_centered.update_time)) or 'has not been centered')
                    print "Localization: UPDATE DIST %s (%s %s)" % (
                                obj.name, other_obj.name, other)
                    print "            : %s is (%s, %s)" % (other_obj.name,
                                nicefloat(other_obj.normalized2_centerX),
                                nicefloat(other_obj.normalized2_centerY))
                # update pose
                self.updatePoseAndCalcDistance(obj)
                new_dist = True
                # OK - It isn't possible to have both centered at once. I'm
                # "enforcing it" - TODO - actually check and error if they both
                # say "centered"
                break
        if not new_dist or not other_obj.centered_self.sighted_centered: return
        world = self._world
        t_end = obj.update_time # since it has just been centered, this is correct
        t_start = other_obj.centered_self.update_time
        moved = world.odometry.movedBetweenTimes(t_start, t_end)
        if self.verbose:
            print "Localization: %s in %d+[0,%3.3f] for %s..>%s" % (
                moved and 'moved' or 'stationary',
                t_start - world.start_time, t_end - t_start,
                other_obj.name, obj.name)
        if not moved:
            if self.updateRobotPosition():
                if self.verbose:
                    print "Localization: UPDATE SELF POSITION"
                events.add(EVENT_WORLD_LOCATION_UPDATED)

        #seeing our goal - opposing is unseen
        if self._world.our_lp.seen and self._world.our_rp.seen:
            self.calc_goal_coord(self._world.our_lp,self._world.our_rp, self._world.opposing_lp, self._world.opposing_rp)

        #seeing opposing goal - our is unseen
        if self._world.opposing_lp.seen and self._world.opposing_rp.seen:
            self.calc_goal_coord(self._world.opposing_lp,self._world.opposing_rp, self._world.our_lp, self._world.our_rp)

    def updatePoseAndCalcDistance(self, obj):
        body_angles = self._world.getBodyAngles()
        inclination_angles = self._world.getInclinationAngles()
        # TODO - pass support leg (common usage is probably during stand,
        # so this won't be a problem - still..)
        self._pose.updateTransforms(body_angles, inclination_angles)
        obj.my_dist = self.calcPostDist(obj)
        if self.verbose:
            print "Localization: %s new dist = %3.1f, vision dists %3.1f, %3.1f" % (
                obj.name, obj.my_dist, obj.dist, obj.focDist)

    def calcPostDist(self, post):
        #print "please add the pix dist"
        #import pdb; pdb.set_trace()
        return self._pose.pixHeightToDistance(post.height, GOAL_POST_CM_HEIGHT)

    def updateRobotPosition(self):
        """ tries to update robot position from current landmarks. return value is success """
        d = CROSSBAR_CM_WIDTH / 2.0
        bottom, top = self._bottom, self._top
        p0 = top.xy
        p1 = bottom.xy
        # TODO - use all dists, compare
        if not hasattr(top, 'my_dist') or not hasattr(bottom, 'my_dist'):
            if self.verbose:
                print "BUG ALERT: we should have my_dist updated at this point."
            return False
        r1, r2, a1 = (top.my_dist, bottom.my_dist, top.bearing)
        # compute distance using r_avg and angle - note that it is not correct
        if abs(r1 - r2) > 2*d:
            if self.verbose:
                print "Localization: Warning: inputs are bad, need to recalculate"
            # This is fun: which value do I throw away? I could start
            # collecting a bunch first, and only if it is well localized (looks
            # like a nice normal distribution) I use it..
            return False
        x, y, theta = xyt_from_two_dist_one_angle(
                r1=r1, r2=r2, a1=a1, d=d, p0=p0, p1=p1)
        min_x, max_x, min_y, max_y = white_limits # This is the WHITE limits - we could be in the green part.. COMPETITION
        if not (min_x <= x <= max_x) or not (min_y <= y <= max_y):
            #import pdb; pdb.set_trace()
            print "LOCALIZATION ERROR - out of White bounds; not updating"
            print "Error value: %3.2f %3.2f %3.2f deg" % (x, y, theta*RAD_TO_DEG)
            return False
        if self.verbose:
            print "Localization: GOT %3.2f %3.2f heading %3.2f deg" % (x, y, theta*RAD_TO_DEG)
        r = self._world.robot
        r.world_x, r.world_y, r.world_heading = x, y, theta
        r.world_position_update_time = self._world.time
        self._history.append((r.world_position_update_time, r.world_x, r.world_y, r.world_heading))
        return True

    def calc_goal_coord(self, sglp, sgrp, uglp, ugrp):
        """
        Update position of unseen goal.
        """
        if HALF_GOAL_SIZE>=sglp.dist or HALF_GOAL_SIZE>=sgrp.dist:
            return

        #debug
        #(x1,y1, theta1) = xyt_from_two_dist_one_angle(200, 250, 0,HALF_GOAL_SIZE , (0, HALF_GOAL_SIZE) ,(0, -HALF_GOAL_SIZE) )

        (x1,y1, theta1) =  xyt_from_two_dist_one_angle(sglp.dist, sgrp.dist, sglp.bearing,HALF_GOAL_SIZE , (0, HALF_GOAL_SIZE) ,(0, -HALF_GOAL_SIZE) )

        if x1 and y1:
            uglp.dist = ((FIELD_SIZE + x1)**2 + (-HALF_GOAL_SIZE + y1)**2)**0.5
            ugrp.dist = ((FIELD_SIZE + x1)**2 + (HALF_GOAL_SIZE + y1)**2)**0.5
            uglp.bearing = asin(abs(-HALF_GOAL_SIZE + y1) / uglp.dist)
            ugrp.bearing = asin(abs(HALF_GOAL_SIZE + y1) / ugrp.dist)
        else:
            #print "NOTICE: localization->calc_goal_coord: x1/y1/theta1 is None"
            pass

