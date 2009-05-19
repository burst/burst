
D2R = DEG_TO_RAD = 0.0174532925199
R2D = RAD_TO_DEG = 1/DEG_TO_RAD


class WalkParameters(list):
    ''' An encapsulation of the walk parameters. I saw a TODO in the actions 
        file that requested this, et voila! '''

    # Constants:
    ShoulderMedian, ShoulderAmplitude, ElbowMedian, ElbowAmplitude, LHipRoll, RHipRoll, HipHeight, TorsoYOrientation, StepLength, StepHeight, StepSide, MaxTurn, ZmpOffsetX, ZmpOffsetY, TimePerStep = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            super(WalkParameters, self).__init__(*args, **kwargs)
        else:
            super(WalkParameters, self).__init__([0.0 for item in xrange(15)])

        for var in ['ShoulderMedian', 'ShoulderAmplitude', 'ElbowMedian', 'ElbowAmplitude']:

            def f(value):
                self[getattr(self, var)] = value * DEG_TO_RAD
            setattr(self, "set"+var+"Deg", f)
            setattr(self, "get"+var+"Deg", lambda: self[getattr(self, var)] * RAD_TO_DEG)

            def f(value):
                self[getattr(self, var)] = value
            setattr(self, "set"+var+"Rad", f)
            setattr(self, "get"+var+"Rad", lambda: self[getattr(self, var)])

        for var in ['LHipRoll', 'RHipRoll', 'TorsoYOrientation']:

            def f(value):
                self[getattr(self, var)] = value
            setattr(self, "set"+var+"Deg", f)
            setattr(self, "get"+var+"Deg", lambda: self[getattr(self, var)])

            def f(value):
                self[getattr(self, var)] = value * RAD_TO_DEG
            setattr(self, "set"+var+"Rad", f)
            setattr(self, "get"+var+"Rad", lambda: self[getattr(self, var)] * DEG_TO_RAD)

    def __str__(self):
        result = str(self[0])
        for i in xrange(1, 15):
            result += ", " + str(self[i])
        return result
