"""
Localization object that belongs to world, and is called once
per step. In charge of updating various positions, world coordinates
and otherwise.
"""

import burst

class Localization(object):
    
    verbose = burst.options.verbose_localization

    def __init__(self, world):
        self._world = world
        # Location of robot (ourselves)
        self._location = None
        # Location of ball
        self._ball_location = None
        self._inclination_vars = ['Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value',
            'Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value']
        self._world.addMemoryVars(self._inclination_vars)

    def calc_events(self, events, deferreds):
        """
        Update position of unseen goal.
        """
        # First, check for each of the goal posts, if it is visibile dead center, then
        # update it's location.
        # Second, if an update occured, and the other post is also updated without any
        # movement in between, we update our location.
        # this, coupled with the localizer which initiates a search for both posts,
        # will ensure an update of the location.
        # Additionally, oppurtunistic updates will be possible (though not expected
        # until we add more landmarks like intersections etc.)
        # On the gripping hand, this is the perfect place to do Particle Filter / Kalman
        # Filter updates from landmakrs, once such code exists.
        
        # We defer updating pose until we actually need it.
        new_dist = False
        left, right = self._world.team.target_posts.left_right
        for obj, other_obj in ((left, right), (right, left)):
            if obj.seen and obj.centered:
                if self.verbose:
                    print "Localization: UPDATE DIST"
                new_dist = True
                # OK - It isn't possible to have both centered at once. I'm
                # "enforcing it" - TODO - actually check and error if they both
                # say "centered"
                break
        if not new_dist: return
        moved = self._world.odometry.movedBetweenTimes(other_obj.newness,
            obj.newness)
        if self.verbose:
            print "Localization: %s in %d+[0,%3.3f] for %s..>%s" % (
                moved and 'moved' or 'stationary',
                other_obj.newness, obj.newness, other_obj._name, obj._name)
        if not moved:
            if self.verbose:
                print "Localization: UPDATE SELF POSITION"

