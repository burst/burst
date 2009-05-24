
from consts import DEG_TO_RAD, RAD_TO_DEG



class WalkParameters(list):
    ''' An encapsulation of the walk parameters. I saw a TODO in the actions 
        file that requested this, et voila! '''

    # Constants:
    (ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude, LHipRoll, RHipRoll, HipHeight, 
    TorsoYOrientation, StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY) = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            super(WalkParameters, self).__init__(*args, **kwargs)
        else:
            super(WalkParameters, self).__init__([0.0 for item in xrange(15)])

    def __str__(self):
        result = str(self[0])
        for i in xrange(1, 14):
            result += ", " + str(self[i])
        return result



# Add some syntactic sugar to the class's objects.
for var in ['ShoulderMedian', 'ShoulderAmplitude', 'ElbowMedian', 'ElbowAmplitude']:

    def f(self, value):
        self[getattr(self, var)] = value * DEG_TO_RAD
    setattr(WalkParameters, "set"+var+"Deg", f)
    setattr(WalkParameters, "get"+var+"Deg", lambda self: self[getattr(self, var)] * RAD_TO_DEG)

    def f(self, value):
        self[getattr(self, var)] = value
    setattr(WalkParameters, "set"+var+"Rad", f)
    setattr(WalkParameters, "get"+var+"Rad", lambda self: self[getattr(self, var)])

for var in ['LHipRoll', 'RHipRoll', 'TorsoYOrientation']:

    def f(self, value):
        self[getattr(self, var)] = value
    setattr(WalkParameters, "set"+var+"Deg", f)
    setattr(WalkParameters, "get"+var+"Deg", lambda self: self[getattr(self, var)])

    def f(self, value):
        self[getattr(self, var)] = value * RAD_TO_DEG
    setattr(WalkParameters, "set"+var+"Rad", f)
    setattr(WalkParameters, "get"+var+"Rad", lambda self: self[getattr(self, var)] * DEG_TO_RAD)
