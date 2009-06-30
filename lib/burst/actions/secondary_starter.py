from burst.behavior import Behavior
from burst_consts import LEFT, RIGHT
import burst.field as field
DELTA_X=1.0
DELTA_Y_LEFT=0.0
DELTA_Y_RIGHT=3.0
class SecondaryStarter(Behavior):

    def __init__(self, actions, direction=LEFT):
        #TODO - super??        
        super(SecondaryStarter, self).__init__(actions, 'SecondaryStarter')
        self._direction = direction

    def _start(self, firstTime=False):
        #TODO - 
        if self._direction == LEFT:
            print "Approaching left side"            
            self._actions.changeLocationRelative(DELTA_X, DELTA_Y_LEFT).onDone(self._doNextAction)
        else:
            print "Approaching right side"            
            self._actions.changeLocationRelative(DELTA_X, DELTA_Y_RIGHT).onDone(self._doNextAction)

    def _stop(self):
        # we assume user uses everything, so we stop everything. Override to have different behavior.
        #self._actions.searcher.stop()
        #self._actions.tracker.stop()
        #self._actions.centerer.stop()
        #self._actions.clearFootsteps()
        #self._actions.localizer.stop()
        return self._actions.succeed(self)

    def _doNextAction(self):
        #TODO - should I put here something?
        return

#TODO - special cases: 
# fallen
# obstructed

