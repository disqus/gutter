from functools import partial

from base import Container, argument  # noqa
import variables

Value = partial(argument, variables.Value)
Boolean = partial(argument, variables.Boolean)
String = partial(argument, variables.String)
Integer = partial(argument, variables.Integer)
Float = partial(argument, variables.Float)
