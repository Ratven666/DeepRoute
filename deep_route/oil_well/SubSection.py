from deep_route.oil_well.Measure import Measure


class SubSection:

    def __init__(self, measure: Measure):
        self.measure = measure

    def __str__(self):
        return self.measure.__repr__()

