import unittest
from nose.tools import *
from gargoyle.client.operators.comparable import *
from gargoyle.client.operators.identity import *
from gargoyle.client.operators.misc import *


class BaseOperator(object):

    def test_has_label(self):
        ok_(self.operator.label)

    def test_has_preposition(self):
        ok_(self.operator.preposition)

    def test_has_applies_to_method(self):
        ok_(self.operator.applies_to)

    @property
    def str(self):
        return str(self.operator)


class TestTruthyCondition(BaseOperator, unittest.TestCase):

    @property
    def operator(self):
        return Truthy()

    def test_applies_to_if_argument_is_truthy(self):
        ok_(self.operator.applies_to(True))
        ok_(self.operator.applies_to("hello"))
        ok_(self.operator.applies_to(False) is False)
        ok_(self.operator.applies_to("") is False)

    def test_str_says_is_truthy(self):
        eq_(self.str, 'is truthy')


class TestEqualsCondition(BaseOperator, unittest.TestCase):

    @property
    def operator(self):
        return Equals(value='Fred')

    def test_applies_to_if_argument_is_equal_to_value(self):
        ok_(self.operator.applies_to('Fred'))
        ok_(self.operator.applies_to('Steve') is False)
        ok_(self.operator.applies_to('') is False)
        ok_(self.operator.applies_to(True) is False)

    @raises(TypeError)
    def test_raises_error_if_not_provided_value(self):
        Equals()

    def test_str_says_is_equal_to_condition(self):
        eq_(self.str, 'is equal to "Fred"')


class TestEnumCondition(BaseOperator, unittest.TestCase):

    @property
    def operator(self):
        return Enum(False, 2.0, '3')

    def test_applies_to_if_argument_in_enum(self):
        ok_(self.operator.applies_to(False))
        ok_(self.operator.applies_to(2.0))
        ok_(self.operator.applies_to(9) is False)
        ok_(self.operator.applies_to("1") is False)
        ok_(self.operator.applies_to(True) is False)

    def test_str_says_it_is_in_possibilities(self):
        eq_(self.str, 'is in "False", "2.0", "3"')


class TestBetweenCondition(BaseOperator, unittest.TestCase):

    @property
    def operator(self, lower=1, higher=100):
        return Between(lower, higher)

    def test_applies_to_if_between_lower_and_upper_bound(self):
        ok_(self.operator.applies_to(0) is False)
        ok_(self.operator.applies_to(1) is False)
        ok_(self.operator.applies_to(2))
        ok_(self.operator.applies_to(99))
        ok_(self.operator.applies_to(100) is False)
        ok_(self.operator.applies_to('steve') is False)

    def test_applies_to_works_with_any_comparable(self):
        animals = Between('cobra', 'orangatang')
        ok_(animals.applies_to('dog'))
        ok_(animals.applies_to('elephant'))
        ok_(animals.applies_to('llama'))
        ok_(animals.applies_to('aardvark') is False)
        ok_(animals.applies_to('whale') is False)
        ok_(animals.applies_to('zebra') is False)

    def test_str_says_between_values(self):
        eq_(self.str, 'is between "1" and "100"')


class TestLessThanCondition(BaseOperator, unittest.TestCase):

    @property
    def operator(self, upper=500):
        return LessThan(upper)

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
        ok_(LessThan('giraffe').applies_to('aardvark'))
        ok_(LessThan('giraffe').applies_to('zebra') is False)
        ok_(LessThan(56.7).applies_to(56))
        ok_(LessThan(56.7).applies_to(56.0))
        ok_(LessThan(56.7).applies_to(57.0) is False)
        ok_(LessThan(56.7).applies_to(56.71) is False)

    def test_str_says_less_than_value(self):
        eq_(self.str, 'is less than "500"')


class TestLessThanOrEqualToOperator(BaseOperator):

    @property
    def operator(self, upper=500):
        return LessThanOrEqualTo(upper)

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
        ok_(LessThanOrEqualTo('giraffe').applies_to('aardvark'))
        ok_(LessThanOrEqualTo('giraffe').applies_to('zebra') is False)
        ok_(LessThanOrEqualTo('giraffe').applies_to('giraffe') is True)
        ok_(LessThanOrEqualTo(56.7).applies_to(56))
        ok_(LessThanOrEqualTo(56.7).applies_to(56.0))
        ok_(LessThanOrEqualTo(56.7).applies_to(56.7))
        ok_(LessThanOrEqualTo(56.7).applies_to(57.0) is False)
        ok_(LessThanOrEqualTo(56.7).applies_to(56.71) is False)

    def test_str_says_less_than_or_equal_to_value(self):
        eq_(self.str, 'is less than or equal to "500"')


class TestMoreThanOperator(BaseOperator, unittest.TestCase):

    @property
    def operator(self, lower=10):
        return MoreThan(lower)

    def test_applies_to_if_value_more_than_argument(self):
        ok_(self.operator.applies_to(float("inf")))
        ok_(self.operator.applies_to(10000))
        ok_(self.operator.applies_to(11))
        ok_(self.operator.applies_to(10) is False)
        ok_(self.operator.applies_to(0) is False)
        ok_(self.operator.applies_to(-100) is False)
        ok_(self.operator.applies_to(float('-inf')) is False)

    def test_works_with_any_comparable(self):
        ok_(MoreThan('giraffe').applies_to('zebra'))
        ok_(MoreThan('giraffe').applies_to('aardvark') is False)
        ok_(MoreThan(56.7).applies_to(57))
        ok_(MoreThan(56.7).applies_to(57.0))
        ok_(MoreThan(56.7).applies_to(56.0) is False)
        ok_(MoreThan(56.7).applies_to(56.71))

    def test_str_says_more_than_value(self):
        eq_(self.str, 'is more than "10"')


class TestMoreThanOrEqualToOperator(BaseOperator, unittest.TestCase):

    @property
    def operator(self, lower=10):
        return MoreThanOrEqualTo(lower)

    def test_applies_to_if_value_more_than_argument(self):
        ok_(self.operator.applies_to(float("inf")))
        ok_(self.operator.applies_to(10000))
        ok_(self.operator.applies_to(11))
        ok_(self.operator.applies_to(10) is True)
        ok_(self.operator.applies_to(0) is False)
        ok_(self.operator.applies_to(-100) is False)
        ok_(self.operator.applies_to(float('-inf')) is False)

    def test_works_with_any_comparable(self):
        ok_(MoreThanOrEqualTo('giraffe').applies_to('zebra'))
        ok_(MoreThanOrEqualTo('giraffe').applies_to('aardvark') is False)
        ok_(MoreThanOrEqualTo('giraffe').applies_to('giraffe'))
        ok_(MoreThanOrEqualTo(56.7).applies_to(57))
        ok_(MoreThanOrEqualTo(56.7).applies_to(57.0))
        ok_(MoreThanOrEqualTo(56.7).applies_to(56.7))
        ok_(MoreThanOrEqualTo(56.7).applies_to(56.0) is False)
        ok_(MoreThanOrEqualTo(56.7).applies_to(56.71))

    def test_str_says_more_than_or_equal_to_value(self):
        eq_(self.str, 'is more than or equal to "10"')


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

    @property
    def operator(self):
        return Percent(50)

    def test_applies_to_percentage_passed_in(self):
        self.assertAlmostEqual(self.successful_runs(1000), 500, delta=50)

    def test_str_says_applies_to_percentage_of_values(self):
        eq_(self.str, 'is in 50.0% of values')


class PercentRangeTest(PercentTest, unittest.TestCase):

    @property
    def operator(self):
        return self.range_of(10, 20)

    def range_of(self, lower, upper):
        return PercentRange(lower, upper)

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
        eq_(self.str, 'is in 10.0 - 20.0% of values')
