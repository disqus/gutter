from functools import partial

from . import variables
from .base import Container, argument  # noqa

Value = partial(argument, variables.Value)
Boolean = partial(argument, variables.Boolean)
String = partial(argument, variables.String)
Integer = partial(argument, variables.Integer)
Float = partial(argument, variables.Float)
