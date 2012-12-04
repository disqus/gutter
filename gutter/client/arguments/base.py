class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class argument(object):

    def __init__(self, variable, getter):
        if issubclass(type(getter), basestring):
            self.getter = lambda self: getattr(self.input, getter)
        else:
            self.getter = getter

        self.variable = variable

    def __get__(self, instance, owner):
        if instance:
            return self.variable(self.getter(instance))
        else:
            return self


class Base(object):
    """
    Base class for Arguments, which are responsible for understanding inputs
    and returning Argument Variables.  Argument variables are compared against
    the Operator inside of a Condition, for deciding if a condition applies to
    the specified input.
    """

    COMPATIBLE_TYPE = None

    def __init__(self, inpt):
        self.input = inpt

    @classproperty
    def arguments(cls):
        return dict(
            (key, value) for key, value in vars(cls).items()
            if type(value) is argument
        )

    @property
    def applies(self):
        return type(self.input) is self.COMPATIBLE_TYPE
