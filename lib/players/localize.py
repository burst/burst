#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init

from burst_util import Deferred, DeferredList

from burst.player import Player
from burst.events import *
from burst.consts import *
from burst.eventmanager import AndEvent, SerialEvent

import burst.kinematics as kinematics
from burst.kinematics import IMAGE_CENTER_X
from burst.field import (GOAL_POST_CM_HEIGHT, CROSSBAR_CM_WIDTH, yellow_goal,
    CROSSBAR_CM_WIDTH)

MAX_PIXELS_FROM_CENTER_FOR_DISTANCE_ESTIMATE = 10 # TODO - calibrate? there is an optimal number.

def singletime(event):
    """ Decorator that is meant to be used on a generator. The generator
    starts, inits and yields. The event is then registered.
    The event fires, the generator is called, returns. Then we
    unregister it.

    Note: specifically meant for methods of Player - we use self as
    first argument, and specifically use self._eventmanager.register
    and self._eventmanager.unregister methods.
    """
    def wrap(f):
        def wrapper(self, *args, **kw):
            gen = f(self, *args, **kw)
            gen.next() # let it init itself
            def onEvent():
                try:
                    gen.next()
                except StopIteration:
                    pass
                except Exception, e:
                    print "CAUGHT EXCEPTION: %s" % e
                self._eventmanager.unregister(event)
                print "singletime: unregistering from %s" % event
            print "singletime: registering to %s" % event
            self._eventmanager.register(event, onEvent)
        return wrapper
    return wrap

# And now for something simpler - just store the event at a handy place
# inside the method that will be using it.
#
# I tried adding register and unregister methods, but for now I'm stumped
# by the fact that this wrapper is called during class construction, and
# so is handed functions and not methods, and so when I call register
# I give the function and not the wrapper method, so when it is finally
# called it complains that it thought it needs to give 0 arguments but
# the callee wants 1 (the self).
def eventhandler(event):
    def wrap(f):
        f.event = event
        return f
    return wrap

class Localize(Player):
    
    def onError(self, result):
        print self._all_data_in.result.getTraceback()

    def onStart(self):
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        print "Please move the head (use naojoints) to have both yellow goal posts"
        print "in the image center, I will print helpful text whenever I think you"
        print "got it right."

        self._pose = kinematics.pose
        self._yellowtop = Deferred()
        self._yellowbottom = Deferred()
        self._all_data_in = DeferredList([self._yellowtop, self._yellowbottom])
        self._all_data_in.addCallback(self.onAvailableInformationForLocationCalculation).addErrback(self.onError)

        self.yellow_top_dist, self.yellow_top_bearing = None, None
        self.yellow_bottom_dist = None

        #for f in [self.onYellowBottomPosChange, self.onYellowTopPosChange]:
        #    self._eventmanager.register(f.event, f)

        self.registerDecoratedEventHandlers()
        
    def registerDecoratedEventHandlers(self):
        # register to events - see singletime
        for f in [f for f in self.__dict__.values() if hasattr(f, 'event')]:
            self._eventmanager.register(f.event, f)

    @eventhandler(EVENT_YGRP_POSITION_CHANGED)
    def onYellowTopPosChange(self):
        obj = self._world.ygrp # Yellow Right is Top - since it's goalie looks towards minus x
        dx = abs(obj.x - IMAGE_CENTER_X)
        print "yellow top - dx = %s" % dx
        if dx < MAX_PIXELS_FROM_CENTER_FOR_DISTANCE_ESTIMATE:
            print "yellow TOP DONE"
            self.yellow_top_dist = self._pose.pixHeightToDistance(obj.height, GOAL_POST_CM_HEIGHT)
            self.yellow_top_bearing = obj.bearing
            self._yellowtop.callback(None)
            self._eventmanager.unregister(self.onYellowTopPosChange.event)

    @eventhandler(EVENT_YGLP_POSITION_CHANGED)
    def onYellowBottomPosChange(self):
        obj = self._world.yglp # Yellow Left is Bottom - since it's goalie looks towards minus x
        dx = abs(obj.x - IMAGE_CENTER_X)
        print "yellow bottom - dx = %s" % dx
        if abs(obj.x - IMAGE_CENTER_X) < MAX_PIXELS_FROM_CENTER_FOR_DISTANCE_ESTIMATE:
            print "yellow BOTTOM DONE"
            self.yellow_bottom_dist = self._pose.pixHeightToDistance(obj.height, GOAL_POST_CM_HEIGHT)
            self._yellowbottom.callback(None)
            self._eventmanager.unregister(self.onYellowBottomPosChange.event)

    def onAvailableInformationForLocationCalculation(self, result):
        print "calculating position"
        d = CROSSBAR_CM_WIDTH / 2.0
        p0 = yellow_goal.top_post.xy
        p1 = yellow_goal.bottom_post.xy
        x, y, theta = self._pose.xyt_from_two_dist_one_angle(
            r1=self.yellow_top_dist, r2=self.yellow_bottom_dist, a1=self.yellow_top_bearing,
            d = d, p0=p0, p1=p1)
        print "GOT %3.3f %3.3f heading %3.3f deg" % (x, y, theta*RAD_TO_DEG)

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Localize).run()

