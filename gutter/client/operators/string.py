from gutter.client.arguments.variables import Base as VariableBase
from gutter.client.operators import Base
from gutter.client.registry import operators


class EqualsStripIgnoreCase(Base):

    name = 'strip_ignorecase_equals'
    group = 'string'
    preposition = 'strip ignore case equal to'
    arguments = ('value',)

    def applies_to(self, argument):
        if isinstance(argument, VariableBase):
            argument = str(argument.value)
        else:
            argument = str(argument)

        return argument.lower().strip() == self.value.lower().strip()

    def __str__(self):
        return '%s "%s"' % (self.preposition, self.value.lower())

operators.register(EqualsStripIgnoreCase)
