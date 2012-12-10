class OperatorInitError(ValueError):

    def __init__(self, argument):
        message = "Missing argument %s to construct operator." % argument
        super(OperatorInitError, self).__init__(message)


class Base(object):

    arguments = ()

    def __init__(self, *args, **kwargs):
        try:
            for argument in self.arguments:
                setattr(self, argument, kwargs.pop(argument))
        except KeyError:
            raise OperatorInitError(argument)

    @property
    def variables(self):
        return vars(self)

    def __eq__(self, other):
        for arg in vars(self).keys():
            if getattr(self, arg) != getattr(other, arg):
                return False

        return True
