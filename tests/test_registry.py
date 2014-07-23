import itertools
import unittest2

from exam.cases import Exam
from exam.decorators import fixture

from gutter.client.operators import (
    Base,
    comparable,
    identity,
    misc,
)
from gutter.client.arguments.base import Container
from gutter.client.registry import Registry

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

    operator = fixture(TestOperator)
    registry = fixture(Registry)

    def test_stores_registered_operator_via_provided_name(self):
        self.registry.operators.register('hello', self.operator)
        self.assertEqual(self.registry.operators['hello'], self.operator)

    def test_raises_exception_if_object_is_not_an_operator(self):
        self.assertRaises(
            ValueError,
            self.registry.operators.register,
            'junk',
            'thing'
        )


class TestArgumentRegistry(Exam, unittest2.TestCase):

    registry = fixture(Registry)

    def test_stores_registered_argument_via_provided_name(self):
        self.registry.arguments.register('test', TestArgument)
        self.assertEqual(self.registry.arguments['test'], TestArgument)

    def test_raises_exception_if_object_is_not_an_argument(self):
        self.assertRaises(
            ValueError,
            self.registry.arguments.register,
            'junk',
            'thing'
        )
