#!/usr/bin/python

#######################################################################################################################

import player_init
from burst.behavior import InitialBehavior
from burst_events import *
from burst_consts import *
import burst.moves.poses as poses
from burst.actions.target_finder import TargetFinder
from math import pi
from burst_consts import DEG_TO_RAD

#######################################################################################################################

debug = True
right = -1
left  = +1
STEP_SIZE = 0.30
VOVA_OFFSET = 50.0

#######################################################################################################################

def log(string):
    if debug:
        print string


def debugged(f):
    def wrapper(*args, **kw):
        print f.__name__#, args, kw
        return f(*args, **kw)
    return wrapper

#######################################################################################################################

class Goalie(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self.sideLeaptTo = left # TODO: Get this from the previous states, since you'll be incorporated into goalie.py.

    # TODO: Once you've leaped and got up, this takes place:
#    @debugged
    def _start(self, firstTime=False):
        # On having gotten up, turn to the other side until you've found goal.
        # TODO: We might want to prop the head a little higher.
        self._actions.moveHead((pi/2)*(-1*self.sideLeaptTo), -40.0*DEG_TO_RAD).onDone(self.closedLoopFindOppositeOwnPost)
 #   @debugged

    def closedLoopFindOppositeOwnPost(self):
        print self._world.our_goal.unknown.seen, self._world.our_lp.seen, self._world.our_rp.seen
        # Decide which goal post you're looking for:
        lookedForGoalPost = self._world.our_goal.unknown
        if self._world.our_lp.seen: lookedForGoalPost = self._world.our_lp
        if self._world.our_rp.seen: lookedForGoalPost = self._world.our_rp
        # If you see that goal post, AND it's close enough to be directly perpendicular to you, :
#        print lookedForGoalPost.seen, lookedForGoalPost.centerX, self.sideLeaptTo*burst_consts.IMAGE_CENTER_X
        print lookedForGoalPost.seen, lookedForGoalPost.bearing, -self.sideLeaptTo*pi/2
        # TODO: I shouldn't use the bearing, as it's more susceptible to noise and miscalculation. Use cetnerX instead.
        pastCenter = lookedForGoalPost.bearing < pi/2 if self.sideLeaptTo == right else lookedForGoalPost.bearing > -pi/2
        if lookedForGoalPost.seen and pastCenter:
            self.onFocusedOnOppositeOwnPost(lookedForGoalPost)
        else:
            self._actions.turn(-STEP_SIZE*self.sideLeaptTo).onDone(self.closedLoopFindOppositeOwnPost)

  #  @debugged
    def onFocusedOnOppositeOwnPost(self, goalpost):
        print "DISTANCE:", goalpost.dist
        self._actions.changeLocationRelativeSideways(0.0, -self.sideLeaptTo*max(goalpost.dist-VOVA_OFFSET, 0.0)).onDone(
            self.onVova)

    def onVova(self):
        print "VOVA"
        self._eventmanager.quit()

#######################################################################################################################

#for attribute in dir(Goalie):
#    if callable(getattr(Goalie, attribute)):
#        setattr(Goalie, attribute, debugged(getattr(Goalie, attribute)))

#######################################################################################################################

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
