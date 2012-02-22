class PercentRange(object):

    label = 'percent_range'
    description = 'Applies if argument hashes to within percent range'

    def __init__(self, lower, upper):
        self.upper = float(upper)
        self.lower = float(lower)

    def applies_to(self, argument):
        if not argument:
            return False
        else:
            return self.lower <= (hash(argument) % 100) < self.upper


class Percent(PercentRange):

    label = 'percent'
    description = 'Applies if argument hashes to <= percent value'

    def __init__(self, percentage):
        self.upper = float(percentage)
        self.lower = 0.0
