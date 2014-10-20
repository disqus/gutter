from gutter.client.operators import Base
from gutter.client.registry import operators


class EqualsCaseInsensitive(Base):

    name = 'case_insensitive_equals'
    group = 'string'
    preposition = 'case insensitive equal to'
    arguments = ('value',)

    def applies_to(self, argument):
        if not isinstance(argument, basestring):
            argument = str(argument)
        return argument.lower() == self.value.lower()

    def __str__(self):
        return '%s "%s"' % (self.preposition, self.value)


operators.register(EqualsCaseInsensitive)