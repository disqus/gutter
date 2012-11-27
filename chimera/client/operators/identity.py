from chimera.client.operators import Base


class Truthy(Base):

    label = 'truthy'
    group = 'identity'
    preposition = 'is'

    def applies_to(self, argument):
        return bool(argument)

    def __str__(self):
        return 'is truthy'
