from gargoyle.client.operators import Base


class Equals(Base):

    label = 'equals'
    group = 'comparable'
    preposition = 'equals'

    def __init__(self, value):
        self.value = value

    def applies_to(self, argument):
        return argument == self.value

    def __str__(self):
        return 'is equal to "%s"' % self.value


class Between(Base):

    label = 'between'
    group = 'comparable'
    preposition = 'is between'

    def __init__(self, lower, higher):
        self.lower = lower
        self.higher = higher

    def applies_to(self, argument):
        return argument > self.lower and argument < self.higher

    def __str__(self):
        return 'is between "%s" and "%s"' % (self.lower, self.higher)


class LessThan(Base):

    label = 'before'
    group = 'comparable'
    preposition = 'is less than'

    def __init__(self, upper_limit):
        self.upper_limit = upper_limit

    def applies_to(self, argument):
        return argument < self.upper_limit

    def __str__(self):
        return 'is less than "%s"' % self.upper_limit


class LessThanOrEqualTo(LessThan):

    label = 'less_than_or_equal_to'
    group = 'comparable'
    preposition = 'is less than or equal to'

    def applies_to(self, argument):
        return argument <= self.upper_limit

    def __str__(self):
        return 'is less than or equal to "%s"' % self.upper_limit


class MoreThan(Base):

    label = 'more_than'
    group = 'comparable'
    preposition = 'is more than'

    def __init__(self, lower_limit):
        self.lower_limit = lower_limit

    def applies_to(self, argument):
        return argument > self.lower_limit

    def __str__(self):
        return 'is more than "%s"' % self.lower_limit


class MoreThanOrEqualTo(MoreThan):

    label = 'more_than_or_equal_to'
    group = 'comparable'
    preposition = 'is more than or equal to'

    def applies_to(self, argument):
        return argument >= self.lower_limit

    def __str__(self):
        return 'is more than or equal to "%s"' % self.lower_limit
