from gutter.client.operators import Base


class Equals(Base):

    name = 'equals'
    group = 'comparable'
    preposition = 'equal to'

    def __init__(self, value):
        self.value = value

    def applies_to(self, argument):
        return argument == self.value

    def __str__(self):
        return 'equal to "%s"' % self.value


class Between(Base):

    name = 'between'
    group = 'comparable'
    preposition = 'between'

    def __init__(self, lower, higher):
        self.lower = lower
        self.higher = higher

    def applies_to(self, argument):
        return argument > self.lower and argument < self.higher

    def __str__(self):
        return 'between "%s" and "%s"' % (self.lower, self.higher)


class LessThan(Base):

    name = 'before'
    group = 'comparable'
    preposition = 'less than'

    def __init__(self, upper_limit):
        self.upper_limit = upper_limit

    def applies_to(self, argument):
        return argument < self.upper_limit

    def __str__(self):
        return 'less than "%s"' % self.upper_limit


class LessThanOrEqualTo(LessThan):

    name = 'less_than_or_equal_to'
    group = 'comparable'
    preposition = 'less than or equal to'

    def applies_to(self, argument):
        return argument <= self.upper_limit

    def __str__(self):
        return 'less than or equal to "%s"' % self.upper_limit


class MoreThan(Base):

    name = 'more_than'
    group = 'comparable'
    preposition = 'more than'

    def __init__(self, lower_limit):
        self.lower_limit = lower_limit

    def applies_to(self, argument):
        return argument > self.lower_limit

    def __str__(self):
        return 'more than "%s"' % self.lower_limit


class MoreThanOrEqualTo(MoreThan):

    name = 'more_than_or_equal_to'
    group = 'comparable'
    preposition = 'more than or equal to'

    def applies_to(self, argument):
        return argument >= self.lower_limit

    def __str__(self):
        return 'more than or equal to "%s"' % self.lower_limit
