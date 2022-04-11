import six

from gutter.client.compat import NoneType


class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class argument(object):

    def __init__(self, variable, getter):
        if issubclass(type(getter), six.string_types):
            self.getter = lambda self: getattr(self.input, getter)
        else:
            self.getter = getter

        self.owner = None
        self.variable = variable

    def __get__(self, instance, owner):
        self.owner = owner

        if instance:
            return self.variable(self.getter(instance))
        else:
            return self

    def __str__(self):
        if self.name:
            return "%s.%s" % (self.owner.__name__, self.name)
        else:
            return repr(self)

    @property
    def name(self):
        for name, attr in vars(self.owner).items():
            if attr is self:
                return name


class Container(object):

    """
    Base class for Arguments, which are responsible for understanding inputs
    and returning Argument Variables.  Argument variables are compared against
    the Operator inside of a Condition, for deciding if a condition applies to
    the specified input.
    """

    COMPATIBLE_TYPE = NoneType

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
        return isinstance(self.input, self.COMPATIBLE_TYPE)
