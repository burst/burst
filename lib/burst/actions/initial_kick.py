from burst.behavior import Behavior
from burst_consts import LEFT, RIGHT
from burst.actions.actionconsts import KICK_TYPE_INSIDE
from burst.actions.approacher import ApproachTarget
import burst.field as field
NEARBALLOFFSET=5.0
class InitialKicker(Behavior):

    def __init__(self, actions, direction=LEFT):
        super(InitialKicker, self).__init__(actions, 'InitialKicker')
        self._direction = direction

    def _start(self, firstTime=False):
        #self._getTargetPos()
        self._doNextAction()

    def _stop(self):
        # we assume user uses everything, so we stop everything. Override to have different behavior.
        #self._actions.searcher.stop()
        #self._actions.tracker.stop()
        #self._actions.centerer.stop()
        #self._actions.clearFootsteps()
        #self._actions.localizer.stop()
        return self._actions.succeed(self)

    def _doNextAction(self):
        #Initial kick logic:
        # 1. Approcah the ball to the "Ball between legs" state
        # 2. Sidekick to the correct direction
        # 3. return
        #ApproachXYHActiveLocalization(
        #    self._actions, field.MIDFIELD_X  - NEARBALLOFFSET , field.MIDFIELD_Y, 0.0).start().onDone(self._onApproacherInsideDone)
        ApproachTarget(self._actions, self._world.ball)

    def _onApproacherInsideDone(self):
        self.log("Approach Done, kicking")
        self._actions.inside_kick(KICK_TYPE_INSIDE, self._direction)


def InitialKickWithSideKick(actions, direction=LEFT):
    initial_kicker = InitialKicker(actions, direction)
    return initial_kicker
