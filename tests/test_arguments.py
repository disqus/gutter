import unittest2
from mock import MagicMock, Mock
from nose.tools import *

from gutter.client.arguments.variables import *
from gutter.client import arguments
from gutter.client.arguments import Container

from exam.decorators import fixture


class MyArguments(Container):
    variable1 = arguments.Value(lambda self: self.input)
    opposite_variable1 = arguments.Value(lambda self: not self.input)
    str_variable = arguments.String('prop')


class TestBase(unittest2.TestCase):

    container = fixture(Container, True)
    subclass_arguments = fixture(MyArguments, True)
    subclass_str_arg = fixture(MyArguments, Mock(prop=45))

    def test_applies_is_false_if_compatible_type_is_none(self):
        eq_(self.container.COMPATIBLE_TYPE, None)
        eq_(self.container.applies, False)

    def applies_is_true_if_input_type_is_compatible_type(self):
        self.container.COMPATIBLE_TYPE = int
        ok_(type(self.container.input) is not int)

        self.assertFalse(self.container.applies)
        self.container.input = 9
        self.assertTrue(self.container.applies)

    def test_argument_variables_defaults_to_nothing(self):
        eq_(self.container.arguments, {})

    def test_variables_only_returns_argument_objects(self):
        eq_(
            MyArguments.arguments,
            dict(
                variable1=MyArguments.variable1,
                opposite_variable1=MyArguments.opposite_variable1,
                str_variable=MyArguments.str_variable
            )
        )

    def test_arguments_work(self):
        ok_(self.subclass_arguments.variable1)

    def test_can_use_string_as_argument(self):
        eq_(self.subclass_str_arg.str_variable, 45)

    def test_str_is_argument_container_plus_argument_name(self):
        eq_(str(MyArguments.variable1), 'MyArguments.variable1')

    def test_owner_is_class_its_in(self):
        eq_(MyArguments.variable1.owner, MyArguments)

    def test_name_is_name_inside_class(self):
        eq_(MyArguments.variable1.name, 'variable1')
        eq_(MyArguments.opposite_variable1.name, 'opposite_variable1')


class BaseVariableTest(object):

    interface_functions = ['__cmp__', '__hash__', '__nonzero__']

    @fixture
    def argument(self):
        return self.klass(self.valid_comparison_value)

    @fixture
    def interface_methods(self):
        return [getattr(self.argument, f) for f in self.interface_functions]

    def test_implements_comparison_methods(self):
        map(ok_, self.interface_methods)

    def test_implements_to_python(self):
        ok_(self.klass.to_python('1'))


class DelegateToValue(object):

    def test_delegates_all_interface_function_to_the_value_passed_in(self):
        value_passed_in = MagicMock()
        value_passed_in.__cmp__ = Mock()
        argument = self.klass(value_passed_in)

        for function in self.interface_functions:
            values_function = getattr(value_passed_in, function)
            arguments_function = getattr(argument, function)

            arguments_function(self.valid_comparison_value)
            values_function.assert_called_once_with(self.valid_comparison_value)


class ValueTest(BaseVariableTest, DelegateToValue, unittest2.TestCase):

    klass = Value
    valid_comparison_value = 'marv'

    def test_to_python_returns_same_object(self):
        variable = 'hello'
        eq_(Value.to_python(variable), variable)


class BooleanTest(BaseVariableTest, DelegateToValue, unittest2.TestCase):

    klass = Boolean
    valid_comparison_value = True
    interface_functions = ['__cmp__', '__nonzero__']

    def test_hashes_its_hash_value_instead_of_value(self):
        boolean = Boolean(True, hash_value='another value')
        assert_not_equals(hash(True), hash(boolean))
        assert_equals(hash('another value'), hash(boolean))

    def test_creates_random_hash_value_if_not_provided(self):
        boolean = Boolean(True)
        assert_not_equals(hash(True), hash(boolean))
        assert_not_equals(hash(None), hash(boolean))

        assert_not_equals(hash(boolean), hash(Boolean(True)))

    def test_to_python_booleans_the_value(self):
        eq_(Boolean.to_python(1), True)
        eq_(Boolean.to_python(0), False)
        eq_(Boolean.to_python('0'), True)


class StringTest(BaseVariableTest, DelegateToValue, unittest2.TestCase):

    klass = String
    valid_comparison_value = 'foobazzle'
    interface_functions = ['__hash__']

    def test_cmp_compares_with_other_value(self):
        eq_(self.argument.__cmp__('zebra'), -1)
        eq_(self.argument.__cmp__('aardvark'), 1)
        eq_(self.argument.__cmp__('foobazzle'), 0)

    def test_nonzero_returns_if_truthy(self):
        ok_(String('hello').__nonzero__() is True)
        ok_(String('').__nonzero__() is False)
        ok_(String('0').__nonzero__() is True)

    def test_to_python_strs_the_value(self):
        eq_(String.to_python(True), 'True')
        eq_(String.to_python('hello'), 'hello')
        eq_(String.to_python(1), '1')


class IntegerTest(BaseVariableTest, DelegateToValue, unittest2.TestCase):

    klass = Integer
    valid_comparison_value = 1

    def test_to_python_ints_the_value(self):
        eq_(Integer.to_python(True), 1)
        eq_(Integer.to_python(1.0), 1)
        eq_(Integer.to_python(1.5), 1)
        eq_(Integer.to_python('1337'), 1337)
