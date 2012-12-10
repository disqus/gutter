import unittest
from nose.tools import *
from gutter.client.operators.comparable import *
from gutter.client.operators.identity import *
from gutter.client.operators.misc import *

from exam.decorators import fixture


class BaseOperator(object):

    def test_has_name(self):
        ok_(self.operator.name)

    def test_has_preposition(self):
        ok_(self.operator.preposition)

    def test_has_applies_to_method(self):
        ok_(self.operator.applies_to)

    def test_has_variables_property(self):
        ok_(hasattr(self.property_class, 'variables'))

    def test_has_arguments_property(self):
        ok_(hasattr(self.property_class, 'arguments'))

    def test_instances_with_identical_properties_are_equals(self):
        eq_(self.make_operator(), self.make_operator())

    @fixture
    def operator(self):
        return self.make_operator()

    @fixture
    def str(self):
        return str(self.operator)

    @fixture
    def property_class(self):
        return type(self.operator)


class TestTruthyCondition(BaseOperator, unittest.TestCase):

    def make_operator(self):
        return Truthy()

    def test_applies_to_if_argument_is_truthy(self):
        ok_(self.operator.applies_to(True))
        ok_(self.operator.applies_to("hello"))
        ok_(self.operator.applies_to(False) is False)
        ok_(self.operator.applies_to("") is False)

    def test_str_says_is_truthy(self):
        eq_(self.str, 'true')

    def test_variables_is_empty_list(self):
        eq_(self.operator.variables, {})

    def test_arguments_is_empty_list(self):
        eq_(self.operator.arguments, ())


class TestEqualsCondition(BaseOperator, unittest.TestCase):

    def make_operator(self):
        return Equals(value='Fred')

    def test_applies_to_if_argument_is_equal_to_value(self):
        ok_(self.operator.applies_to('Fred'))
        ok_(self.operator.applies_to('Steve') is False)
        ok_(self.operator.applies_to('') is False)
        ok_(self.operator.applies_to(True) is False)

    @raises(KeyError)
    def test_raises_error_if_not_provided_value(self):
        Equals()

    def test_str_says_is_equal_to_condition(self):
        eq_(self.str, 'equal to "Fred"')

    def test_variables_is_just_a_single_value(self):
        eq_(self.operator.variables, dict(value='Fred'))

    def test_arguments_is_value(self):
        eq_(self.operator.arguments, ('value',))


class TestBetweenCondition(BaseOperator, unittest.TestCase):

    def make_operator(self, lower=1, higher=100):
        return Between(lower_limit=lower, upper_limit=higher)

    def test_applies_to_if_between_lower_and_upper_bound(self):
        ok_(self.operator.applies_to(0) is False)
        ok_(self.operator.applies_to(1) is False)
        ok_(self.operator.applies_to(2))
        ok_(self.operator.applies_to(99))
        ok_(self.operator.applies_to(100) is False)
        ok_(self.operator.applies_to('steve') is False)

    def test_applies_to_works_with_any_comparable(self):
        animals = Between(lower_limit='cobra', upper_limit='orangatang')
        ok_(animals.applies_to('dog'))
        ok_(animals.applies_to('elephant'))
        ok_(animals.applies_to('llama'))
        ok_(animals.applies_to('aardvark') is False)
        ok_(animals.applies_to('whale') is False)
        ok_(animals.applies_to('zebra') is False)

    def test_str_says_between_values(self):
        eq_(self.str, 'between "1" and "100"')

    def test_variables_is_just_a_lower_and_higher(self):
        eq_(self.operator.variables, dict(lower_limit=1, upper_limit=100))


class TestLessThanCondition(BaseOperator, unittest.TestCase):

    def make_operator(self, upper=500):
        return LessThan(upper_limit=upper)

    def test_applies_to_if_value_less_than_argument(self):
        ok_(self.operator.applies_to(float("-inf")))
        ok_(self.operator.applies_to(-50000))
        ok_(self.operator.applies_to(-1))
        ok_(self.operator.applies_to(0))
        ok_(self.operator.applies_to(499))
        ok_(self.operator.applies_to(500) is False)
        ok_(self.operator.applies_to(10000) is False)
        ok_(self.operator.applies_to(float("inf")) is False)

    def test_works_with_any_comparable(self):
        ok_(LessThan(upper_limit='giraffe').applies_to('aardvark'))
        ok_(LessThan(upper_limit='giraffe').applies_to('zebra') is False)
        ok_(LessThan(upper_limit=56.7).applies_to(56))
        ok_(LessThan(upper_limit=56.7).applies_to(56.0))
        ok_(LessThan(upper_limit=56.7).applies_to(57.0) is False)
        ok_(LessThan(upper_limit=56.7).applies_to(56.71) is False)

    def test_str_says_less_than_value(self):
        eq_(self.str, 'less than "500"')

    def test_variables_is_upper_limit(self):
        eq_(self.operator.variables, dict(upper_limit=500))


class TestLessThanOrEqualToOperator(BaseOperator):

    def make_operator(self, upper=500):
        return LessThanOrEqualTo(upper_limit=upper)

    def test_applies_if_value_is_less_than_or_equal_to_argument(self):
        ok_(self.operator.applies_to(float("-inf")))
        ok_(self.operator.applies_to(-50000))
        ok_(self.operator.applies_to(-1))
        ok_(self.operator.applies_to(0))
        ok_(self.operator.applies_to(499))
        ok_(self.operator.applies_to(500) is True)
        ok_(self.operator.applies_to(10000) is False)
        ok_(self.operator.applies_to(float("inf")) is False)

    def test_works_with_any_comparable(self):
        ok_(LessThanOrEqualTo(upper_limit='giraffe').applies_to('aardvark'))
        ok_(LessThanOrEqualTo(upper_limit='giraffe').applies_to('zebra') is False)
        ok_(LessThanOrEqualTo(upper_limit='giraffe').applies_to('giraffe') is True)
        ok_(LessThanOrEqualTo(upper_limit=56.7).applies_to(56))
        ok_(LessThanOrEqualTo(upper_limit=56.7).applies_to(56.0))
        ok_(LessThanOrEqualTo(upper_limit=56.7).applies_to(56.7))
        ok_(LessThanOrEqualTo(upper_limit=56.7).applies_to(57.0) is False)
        ok_(LessThanOrEqualTo(upper_limit=56.7).applies_to(56.71) is False)

    def test_str_says_less_than_or_equal_to_value(self):
        eq_(self.str, 'less than or equal to "500"')

    def test_variables_is_upper_limit(self):
        eq_(self.operator.variables, dict(upper_limit=500))


class TestMoreThanOperator(BaseOperator, unittest.TestCase):

    def make_operator(self, lower=10):
        return MoreThan(lower_limit=lower)

    def test_applies_to_if_value_more_than_argument(self):
        ok_(self.operator.applies_to(float("inf")))
        ok_(self.operator.applies_to(10000))
        ok_(self.operator.applies_to(11))
        ok_(self.operator.applies_to(10) is False)
        ok_(self.operator.applies_to(0) is False)
        ok_(self.operator.applies_to(-100) is False)
        ok_(self.operator.applies_to(float('-inf')) is False)

    def test_works_with_any_comparable(self):
        ok_(MoreThan(lower_limit='giraffe').applies_to('zebra'))
        ok_(MoreThan(lower_limit='giraffe').applies_to('aardvark') is False)
        ok_(MoreThan(lower_limit=56.7).applies_to(57))
        ok_(MoreThan(lower_limit=56.7).applies_to(57.0))
        ok_(MoreThan(lower_limit=56.7).applies_to(56.0) is False)
        ok_(MoreThan(lower_limit=56.7).applies_to(56.71))

    def test_str_says_more_than_value(self):
        eq_(self.str, 'more than "10"')

    def test_variables_is_lower_limit(self):
        eq_(self.operator.variables, dict(lower_limit=10))


class TestMoreThanOrEqualToOperator(BaseOperator, unittest.TestCase):

    def make_operator(self, lower=10):
        return MoreThanOrEqualTo(lower_limit=lower)

    def test_applies_to_if_value_more_than_argument(self):
        ok_(self.operator.applies_to(float("inf")))
        ok_(self.operator.applies_to(10000))
        ok_(self.operator.applies_to(11))
        ok_(self.operator.applies_to(10) is True)
        ok_(self.operator.applies_to(0) is False)
        ok_(self.operator.applies_to(-100) is False)
        ok_(self.operator.applies_to(float('-inf')) is False)

    def test_works_with_any_comparable(self):
        ok_(MoreThanOrEqualTo(lower_limit='giraffe').applies_to('zebra'))
        ok_(MoreThanOrEqualTo(lower_limit='giraffe').applies_to('aardvark') is False)
        ok_(MoreThanOrEqualTo(lower_limit='giraffe').applies_to('giraffe'))
        ok_(MoreThanOrEqualTo(lower_limit=56.7).applies_to(57))
        ok_(MoreThanOrEqualTo(lower_limit=56.7).applies_to(57.0))
        ok_(MoreThanOrEqualTo(lower_limit=56.7).applies_to(56.7))
        ok_(MoreThanOrEqualTo(lower_limit=56.7).applies_to(56.0) is False)
        ok_(MoreThanOrEqualTo(lower_limit=56.7).applies_to(56.71))

    def test_str_says_more_than_or_equal_to_value(self):
        eq_(self.str, 'more than or equal to "10"')

    def test_variables_is_lower_limit(self):
        eq_(self.operator.variables, dict(lower_limit=10))


class PercentTest(BaseOperator):

    class FalseyObject(object):

        def __nonzero__(self):
            return False

    def successful_runs(self, number):
        runs = map(self.operator.applies_to, range(1000))
        return len(filter(bool, runs))

    def test_returns_false_if_argument_is_falsey(self):
        eq_(self.operator.applies_to(False), False)
        eq_(self.operator.applies_to(self.FalseyObject()), False)


class PercentageTest(PercentTest, unittest.TestCase):

    def make_operator(self):
        return Percent(percentage=50)

    def test_applies_to_percentage_passed_in(self):
        self.assertAlmostEqual(self.successful_runs(1000), 500, delta=50)

    def test_str_says_applies_to_percentage_of_values(self):
        eq_(self.str, 'in 50.0% of values')

    def test_variables_is_percentage(self):
        eq_(self.operator.variables, dict(percentage=50))


class PercentRangeTest(PercentTest, unittest.TestCase):

    def make_operator(self):
        return self.range_of(10, 20)

    def range_of(self, lower, upper):
        return PercentRange(lower_limit=lower, upper_limit=upper)

    def test_can_apply_to_a_certain_percent_range(self):
        self.assertAlmostEqual(self.successful_runs(1000), 100, delta=20)

    def test_percentage_range_does_not_overlap(self):
        bottom_10 = self.range_of(0, 10)
        next_10 = self.range_of(10, 20)

        for i in range(1, 500):
            bottom = bottom_10.applies_to(i)
            next = next_10.applies_to(i)
            assert_false(bottom is next is True)

    def test_str_says_applies_to_percentage_range_of_values(self):
        eq_(self.str, 'in 10.0 - 20.0% of values')

    def test_variables_is_lower_and_upper(self):
        eq_(self.operator.variables, dict(lower_limit=10, upper_limit=20))
