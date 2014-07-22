from gutter.client.operators import Base
from gutter.client.registry import operators


class Truthy(Base):

    name = 'true'
    group = 'identity'
    preposition = 'true'

    def applies_to(self, argument):
        return bool(argument)

    def __str__(self):
        return 'true'


operators.register(Truthy)
