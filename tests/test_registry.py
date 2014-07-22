import itertools
import unittest2
from copy import copy

from exam.cases import Exam
from exam.decorators import around

from gutter.client.operators import (
    Base,
    comparable,
    identity,
    misc,
)
from gutter.client.arguments.base import Container
from gutter.client import registry

def all_operators_in(module):
    for _, obj in vars(module).iteritems():
        try:
            if issubclass(obj, Base) and obj is not Base:
                yield obj
        except TypeError:
            pass


ALL_OPERATORS = itertools.chain(
    *map(all_operators_in, (comparable, identity, misc))
)


class TestOperator(Base):
    name = 'test_name'


class TestArgument(Container):
    pass


class TestOperatorRegistry(Exam, unittest2.TestCase):

    @around
    def preserve_registry(self):
        original = registry.operators
        registry.operators = copy(registry.operators)
        yield
        registry.operators = original

    def test_has_default_operators_registered_by_default(self):
        for operator in ALL_OPERATORS:
            self.assertEqual(operator, registry.operators[operator.name])

    def test_stores_registered_operator_via_provided_name(self):
        registry.operators.register('hello', TestOperator)
        self.assertEqual(registry.operators['hello'], TestOperator)

    def test_uses_operator_name_if_not_provided_one(self):
        registry.operators.register(TestOperator)
        self.assertEqual(registry.operators['test_name'], TestOperator)

    def test_raises_exception_if_object_is_not_an_operator(self):
        self.assertRaises(
            ValueError,
            registry.operators.register,
            'junk',
            'thing'
        )


class TestArgumentRegistry(Exam, unittest2.TestCase):

    @around
    def preserve_registry(self):
        original = registry.arguments
        registry.arguments = copy(registry.arguments)
        yield
        registry.arguments = original

    def test_stores_registered_argument_via_provided_name(self):
        registry.arguments.register('test', TestArgument)
        self.assertEqual(registry.arguments['test'], TestArgument)

    def test_raises_exception_if_object_is_not_an_argument(self):
        self.assertRaises(
            ValueError,
            registry.arguments.register,
            'junk',
            'thing'
        )
