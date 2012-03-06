class PercentRange(object):

    label = 'percent_range'
    group = 'misc'
    preposition = 'is in the percentage range'

    def __init__(self, lower, upper):
        self.upper = float(upper)
        self.lower = float(lower)

    def applies_to(self, argument):
        if not argument:
            return False
        else:
            return self.lower <= (hash(argument) % 100) < self.upper

    def __str__(self):
        return 'is in %s - %s%% of values' % (self.lower, self.upper)


class Percent(PercentRange):

    label = 'percent'
    group = 'misc'
    preposition = 'is within the percentage'

    def __init__(self, percentage):
        self.upper = float(percentage)
        self.lower = 0.0

    def __str__(self):
        return 'is in %s%% of values' % self.upper
