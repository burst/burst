#!/usr/bin/python

# import player_init MUST BE THE FIRST LINE
import player_init
from burst_util import (BurstDeferred, calculate_middle, calculate_relative_pos, polar2cart, cart2polar)
from burst.behavior import InitialBehavior
from burst_events import *
from burst.moves import *
from burst_consts import *
from burst.eventmanager import AndEvent, SerialEvent
from burst.behavior_params import (KICK_X_OPT, KICK_Y_OPT,
                                   KICK_X_MIN, KICK_X_MAX, KICK_Y_MIN, KICK_Y_MAX,
                                   BALL_IN_KICKING_AREA, BALL_BETWEEN_LEGS, BALL_FRONT_NEAR, BALL_FRONT_FAR,  BALL_SIDE_NEAR, BALL_SIDE_FAR, BALL_DIAGONAL)
from burst_consts import LEFT, RIGHT

def pr(s):
    print s

class KickTest(InitialBehavior):

    def __init__(self, actions):
        InitialBehavior.__init__(self, actions=actions, name=self.__class__.__name__)

    def _start(self, firstTime=False):
        #self._eventmanager.register(self.onStep, EVENT_STEP)
        #    print "setting shared memory to verbose mode"
        #    self._world._shm.verbose = True
        self.startWaiting()
        #self.searchBall()
        #self._actions.kick(kick_type=burst.actions.KICK_TYPE_STRAIGHT,kick_leg=LEFT)
        self._actions.adjusted_straight_kick(LEFT, 0.0)

        #        print burst.moves.getGreatKick()
        self._max = 30
        self._count = 0


    def startWaiting(self):
        print "doNothing: Starting to wait"
        self._eventmanager.callLater(15.0, self.onTimeout)

    def onStep(self):
        self._count += 1
        if self._count < self._max: return
        self._count = 0
        #print "donothing: ball dist is %s" % self._world.ball.dist
        #print "donothing: top_yellow dist is %s" % self._world.opposing_rp.dist
        #print "donothing: bottom_yellow dist is %s" % self._world.opposing_lp.dist

    def onTimeout(self):
        print "timed out at t = %s" % self._world.time
        self._eventmanager.unregister(self.onStep)
#           self._actions.sitPoseAndRelax().onDone(self.onQuit)

    def onQuit(self):
        print "doNothing: quiting"
        self._eventmanager.quit()

    def searchBall(self):
        self._actions.tracker.stop()
        self._actions.search([self._world.ball]).onDone(self.onSearchOver)

    def onSearchOver(self):
        print "Search over"
        # if we got here, all searched objects (currently: ball) are assumed to be found.
        self._actions.track(self._world.ball, self.onLostBall)
        self.kp = True
        # for now, just directly approach ball and kick it wherever
        ballBearing = self._world.ball.bearing
        ballDist = self._world.ball.distSmoothed
        (ball_x, ball_y) = polar2cart(ballDist, ballBearing)
        print "ball_x: %3.3fcm, ball_y: %3.3fcm" % (ball_x, ball_y)
        # determine kicking leg
        side = ballBearing < 0 # 0 = LEFT, 1 = RIGHT
        if (side == LEFT): print "LEFT"
        else: print "RIGHT"


        ball_location = self.calcBallArea(ball_x, ball_y, side)
        DEBUG_AREA = ('BALL_IN_KICKING_AREA', 'BALL_BETWEEN_LEGS', 'BALL_FRONT_NEAR', 'BALL_FRONT_FAR', 'BALL_SIDE_NEAR', 'BALL_SIDE_FAR', 'BALL_DIAGONAL')
        print "AREA: %s" % DEBUG_AREA[ball_location]
        self._actions.kick(kick_type=burst.actions.KICK_TYPE_STRAIGHT,kick_leg=LEFT, kick_offset=0.2)


    def onLostBall(self):
        # TODO: add ball lost handling
        print "BALL LOST, clearing footsteps"
        #self._actions.clearFootsteps() # TODO: Check if possible to do this via post
        self.kp = None
        self.doNextAction()



    def calcBallArea(self, ball_x, ball_y, side):
        if (ball_x <= KICK_X_MAX[side]) and (abs(KICK_Y_MIN[side]) < abs(ball_y) <= abs(KICK_Y_MAX[side])): #KICK_X_MIN[side] <
            return BALL_IN_KICKING_AREA
        elif KICK_Y_MAX[RIGHT] < ball_y < KICK_Y_MAX[LEFT]:
            if ball_x <= KICK_X_MAX[side]:
                return BALL_BETWEEN_LEGS
            elif ball_x <= KICK_X_MAX[side]*3/2:
                return BALL_FRONT_NEAR
            else:
                return BALL_FRONT_FAR
        else: #if (ball_y > KICK_Y_MAX[LEFT] or ball_y < KICK_Y_MAX[RIGHT]):
            if ball_x <= KICK_X_MAX[side]:
                return BALL_SIDE_NEAR
            else: #ball_x > KICK_X_MAX[side]
                return BALL_DIAGONAL
if __name__ == '__main__':
    import burst
    from burst.eventmanager import MainLoop
    MainLoop(KickTest).run()

