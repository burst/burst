"""
Localization object that belongs to world, and is called once
per step. In charge of updating various positions, world coordinates
and otherwise.
"""

class Localization(object):
    
    def __init__(self, world):
        self._world = world

    def calc_events(self, events, deferreds):
        """
        Update position of unseen goal.
        """
        pass

