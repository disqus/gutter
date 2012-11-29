import types


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

    @property
    def variables(self):
        things = (getattr(type(self), prop) for prop in dir(type(self)))
        return filter(is_valid_variable, things)

    @property
    def applies(self):
        return type(self._input) is self.COMPATIBLE_TYPE
