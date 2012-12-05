from gutter.client.operators import Base


class PercentRange(Base):

    label = 'percent_range'
    group = 'misc'
    preposition = 'in the percentage range of'

    def __init__(self, lower, upper):
        self.upper = float(upper)
        self.lower = float(lower)

    def applies_to(self, argument):
        if not argument:
            return False
        else:
            return self.lower <= (hash(argument) % 100) < self.upper

    def __str__(self):
        return 'in %s - %s%% of values' % (self.lower, self.upper)


class Percent(PercentRange):

    label = 'percent'
    group = 'misc'
    preposition = 'within the percentage of'

    def __init__(self, percentage):
        self.upper = float(percentage)
        self.lower = 0.0

    @property
    def arguments(self):
        return dict(percentage=self.upper)

    def __str__(self):
        return 'in %s%% of values' % self.upper
