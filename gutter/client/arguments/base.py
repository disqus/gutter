import types


class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def is_valid_variable(thing):
    return (
        isinstance(thing, types.MethodType) and
        not thing.__name__.startswith('_')
    )


class Base(object):
    """
    Base class for Arguments, which are responsible for understanding inputs
    and returning Argument Variables.  Argument variables are compared against
    the Operator inside of a Condition, for deciding if a condition applies to
    the specified input.
    """

    COMPATIBLE_TYPE = None

    def __init__(self, inpt):
        self._input = inpt

    @classproperty
    def variables(cls):
        return [
            getattr(cls, key) for key, value in vars(cls).items()
            if callable(value) and is_valid_variable(getattr(cls, key))
        ]

    @property
    def applies(self):
        return type(self._input) is self.COMPATIBLE_TYPE
