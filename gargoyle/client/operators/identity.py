class Truthy(object):

    label = 'truthy'
    group = 'identity'
    preposition = 'is'

    def applies_to(self, argument):
        return bool(argument)

    def __str__(self):
        return 'is truthy'


class Enum(object):

    label = 'enum'
    group = 'identity'
    preposition = 'is in'

    def __init__(self, *possibilities):
        self.possibilities = possibilities

    def applies_to(self, argument):
        return argument in self.possibilities

    def __str__(self):
        quoted = ['"%s"' % str(p) for p in self.possibilities]
        return "is in %s" % ", ".join(quoted)
