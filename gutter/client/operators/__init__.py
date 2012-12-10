class Base(object):

    arguments = ()

    def __init__(self, *args, **kwargs):
        for argument in self.arguments:
            setattr(self, argument, kwargs.pop(argument))

    @property
    def variables(self):
        return vars(self)

    def __eq__(self, other):
        for arg in vars(self).keys():
            if getattr(self, arg) != getattr(other, arg):
                return False

        return True
