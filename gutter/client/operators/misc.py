from gutter.client.operators import Base


class PercentRange(Base):

    name = 'percent_range'
    group = 'misc'
    preposition = 'in the percentage range of'
    arguments = ('lower_limit', 'upper_limit')

    def __init__(self, lower_limit, upper_limit):
        self.upper_limit = float(upper_limit)
        self.lower_limit = float(lower_limit)

    def applies_to(self, argument):
        if not argument:
            return False
        else:
            return self.lower_limit <= (hash(argument) % 100) < self.upper_limit

    def __str__(self):
        return 'in %s - %s%% of values' % (self.lower_limit, self.upper_limit)


class Percent(PercentRange):

    name = 'percent'
    group = 'misc'
    preposition = 'within the percentage of'
    arguments = ('percentage',)

    def __init__(self, percentage):
        self.upper_limit = float(percentage)
        self.lower_limit = 0.0

    @property
    def variables(self):
        return dict(percentage=self.upper_limit)

    def __str__(self):
        return 'in %s%% of values' % self.upper_limit
