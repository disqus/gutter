from gutter.client.operators import Base
from gutter.client.registry import operators


class Equals(Base):

    name = 'equals'
    group = 'comparable'
    preposition = 'equal to'
    arguments = ('value',)

    def applies_to(self, argument):
        return argument == self.value

    def __str__(self):
        return 'equal to "%s"' % self.value


class Between(Base):

    name = 'between'
    group = 'comparable'
    preposition = 'between'
    arguments = ('lower_limit', 'upper_limit')

    def applies_to(self, argument):
        return argument > self.lower_limit and argument < self.upper_limit

    def __str__(self):
        return 'between "%s" and "%s"' % (self.lower_limit, self.upper_limit)


class LessThan(Base):

    name = 'before'
    group = 'comparable'
    preposition = 'less than'
    arguments = ('upper_limit',)

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
    arguments = ('lower_limit',)

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


operators.register(Equals)
operators.register(Between)
operators.register(LessThan)
operators.register(LessThanOrEqualTo)
operators.register(MoreThan)
operators.register(MoreThanOrEqualTo)
