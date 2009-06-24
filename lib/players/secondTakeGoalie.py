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

#TODO: Align according to opposite goal.

#######################################################################################################################

def log(string):
    if debug:
        print string


def debugged(f):
    def wrapper(*args, **kw):
        print f.__name__, args, kw
        return f(*args, **kw)
    return wrapper

#######################################################################################################################

class Goalie(InitialBehavior):

#    @debugged
    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__, initial_pose=poses.SIT_POS)
        self.sideLeaptTo = left # TODO: Get this from the previous states, since you'll be incorporated into goalie.py.

    # TODO: Once you've leaped and got up, this takes place:
#    @debugged
    def _start(self, firstTime=False):
        print "_start"
        # On having gotten up, turn to the other side until you've found goal.
        # TODO: We might want to prop the head a little higher.
        self._actions.moveHead((pi/2)*(-1*self.sideLeaptTo), -40.0*DEG_TO_RAD).onDone(self.findOppositeOwnPost)

#    @debugged
    def findOppositeOwnPost(self):
        print "findOppositeOwnPost"
        self._eventmanager.register(self.vova, EVENT_STEP)
        self._actions.turn(-self.sideLeaptTo*2*pi)

#    @debugged
    def vova(self):
        lookedForGoalPost = self._world.our_goal.unknown
        if self._world.our_lp.seen: lookedForGoalPost = self._world.our_lp
        if self._world.our_rp.seen: lookedForGoalPost = self._world.our_rp
        pastCenter = lookedForGoalPost.bearing < pi/2 if self.sideLeaptTo == right else lookedForGoalPost.bearing > -pi/2
        if lookedForGoalPost.seen and pastCenter:
            print "vova (triggered)"
            self._eventmanager.unregister(self.vova, EVENT_STEP)
            self._actions.clearFootsteps().onDone(lambda e, lookedForGoalPost=lookedForGoalPost: self.onFocusedOnOppositeOwnPost(lookedForGoalPost))

#    @debugged
    def onFocusedOnOppositeOwnPost(self, goalpost):
        print "onFocusedOnOppositeOwnPost"
        print "DISTANCE:", goalpost.dist
        self._actions.executeMove(poses.STRAIGHT_WALK_INITIAL_POSE).onDone(
            lambda: self._actions.moveHead((pi/2)*(-1*self.sideLeaptTo), -40.0*DEG_TO_RAD).onDone(
            lambda: self._actions.changeLocationRelativeSideways(0.0, -self.sideLeaptTo*max(goalpost.dist-VOVA_OFFSET, 0.0)).onDone(
            lambda: self._actions.moveHead(0.0, -40.0*DEG_TO_RAD).onDone(self.onVova))))

#    @debugged
    def onVova(self):
        print 'onVova'
        self._eventmanager.register(self.alignmentAgainstOppositeGoalTester, EVENT_STEP)
        self._actions.turn(self.sideLeaptTo*2*pi)

#    @debugged
    def alignmentAgainstOppositeGoalTester(self):
#        print 'alignmentAgainstOppositeGoalTester'
        seenOppositePosts = filter(lambda obj: obj.seen, [self._world.opposing_goal.unknown, self._world.opposing_lp, self._world.opposing_rp])
        aligned = lambda obj: obj.centerX > burst_consts.IMAGE_CENTER_X if self.sideLeaptTo == left else obj.centerX < burst_consts.IMAGE_CENTER_X
        if any(map(aligned, seenOppositePosts)):
            self._eventmanager.unregister(self.alignmentAgainstOppositeGoalTester, EVENT_STEP)
            self._actions.clearFootsteps().onDone(lambda e: self.onAligned())

    def onAligned(self):
        print "ALIGNED!"
        # Intentionaly, no self._eventmanager.quit()



#######################################################################################################################

#for attribute in dir(Goalie):
#    if callable(getattr(Goalie, attribute)):
#        setattr(Goalie, attribute, debugged(getattr(Goalie, attribute)))

#######################################################################################################################

if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(Goalie).run()
