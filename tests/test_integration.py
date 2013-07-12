import unittest2
from nose.tools import *

import zlib

from redis import Redis
from durabledict.redis import RedisDict

from gutter.client.operators.comparable import *
from gutter.client.operators.identity import *
from gutter.client.operators.misc import *
from gutter.client.models import Switch, Condition, Manager
from gutter.client import arguments
from gutter.client.arguments.variables import Value, Boolean, String
from gutter.client import signals

from exam.decorators import fixture, before, after
from exam.cases import Exam


class deterministicstring(str):
    """
    Since the percentage-based conditions rely on the hash value from their
    arguments, we use this special deterministicstring class to return
    deterministic string values from the crc32 of itself.
    """

    def __hash__(self):
        return zlib.crc32(self)


class User(object):

    def __init__(self, name, age, location='San Francisco', married=False):
        self.name = name
        self.age = age
        self.location = location
        self.married = married


class UserArguments(arguments.Container):

    COMPATIBLE_TYPE = User

    name = arguments.String(lambda self: self.input.name)
    age = arguments.Value(lambda self: self.input.age)
    location = arguments.String(lambda self: self.input.location)
    married = arguments.Boolean(lambda self: self.input.married)


class TestIntegration(Exam, unittest2.TestCase):

    class Callback(object):

        def __init__(self):
            self.register_calls = []
            self.unregister_calls = []
            self.update_calls = []

        def switch_added(self, switch):
            self.register_calls.append(switch)

        def switch_removed(self, switch):
            self.unregister_calls.append(switch)

        def switch_updated(self, switch):
            self.update_calls.append((switch, switch.changes))

    class inputs(object):

        def __init__(self, manager, *inputs):
            self.manager = manager
            self.manager.input(*inputs)

        def __enter__(self):
            return self

        def active(self, *args, **kwargs):
            return self.manager.active(*args, **kwargs)

        def __exit__(self, type, value, traceback):
            self.manager.flush()

    callback = fixture(Callback)

    @fixture
    def manager(self):
        return Manager(storage=dict())

    @before
    def build_objects(self):
        self.setup_inputs()
        self.setup_conditions()
        self.setup_switches()

    @after
    def reset_objects(self):
        signals.switch_registered.reset()
        signals.switch_unregistered.reset()
        signals.switch_updated.reset()

    def setup_inputs(self):
        self.jeff = User(deterministicstring('jeff'), 21)
        self.frank = User(deterministicstring('frank'), 10, location="Seattle")
        self.larry = User(deterministicstring('bill'), 70, location="Yakima", married=True)
        self.timmy = User(deterministicstring('timmy'), 12)
        self.steve = User(deterministicstring('timmy'), 19)

    def setup_conditions(self):
        self.age_65_and_up = Condition(UserArguments, 'age', MoreThanOrEqualTo(lower_limit=65))
        self.age_under_18 = Condition(UserArguments, 'age', LessThan(upper_limit=18))
        self.age_not_under_18 = Condition(UserArguments, 'age', LessThan(upper_limit=18), negative=True)
        self.age_21_plus = Condition(UserArguments, 'age', MoreThanOrEqualTo(lower_limit=21))
        self.age_between_13_and_18 = Condition(UserArguments, 'age', Between(lower_limit=13, upper_limit=18))

        self.in_sf = Condition(UserArguments, 'location', Equals(value='San Francisco'))
        self.has_location = Condition(UserArguments, 'location', Truthy())

        self.ten_percent = Condition(UserArguments, 'name', Percent(percentage=10))
        self.upper_50_percent = Condition(UserArguments, 'name', PercentRange(lower_limit=50, upper_limit=100))

    def setup_switches(self):
        self.add_switch('can drink', condition=self.age_21_plus)
        self.add_switch('can drink in europe', condition=self.age_21_plus, state=Switch.states.GLOBAL)
        self.add_switch('can drink:wine', condition=self.in_sf, concent=True)
        self.add_switch('retired', condition=self.age_65_and_up)
        self.add_switch('can vote', condition=self.age_not_under_18)
        self.add_switch('teenager', condition=self.age_between_13_and_18)
        self.add_switch('SF resident', condition=self.in_sf)
        self.add_switch('teen or in SF', self.age_between_13_and_18, self.in_sf)
        self.add_switch('teen and in SF', self.age_between_13_and_18,
                        self.has_location, compounded=True)
        self.add_switch('10 percent', self.ten_percent)
        self.add_switch('Upper 50 percent', self.upper_50_percent)

    def add_switch(self, name, condition=None, *conditions, **kwargs):
        switch = Switch(name, compounded=kwargs.get('compounded', False))
        switch.state = kwargs.get('state', Switch.states.SELECTIVE)
        conditions = list(conditions)

        if condition:
            conditions.append(condition)

        [switch.conditions.append(c) for c in conditions]
        kwargs.get('manager', self.manager).register(switch)
        return switch

    def test_basic_switches_work_with_conditions(self):
        with self.inputs(self.manager, self.larry) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('can vote') is True)
            ok_(context.active('SF resident') is False)
            ok_(context.active('retired') is True)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

        with self.inputs(self.manager, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('can vote') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('teenager') is False)
            ok_(context.active('teen or in SF') is True)
            ok_(context.active('teen and in SF') is False)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

        with self.inputs(self.manager, self.frank) as context:
            ok_(context.active('can drink') is False)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('can vote') is False)
            ok_(context.active('teenager') is False)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

    def test_can_use_extra_inputs_to_active(self):
        with self.inputs(self.manager, self.frank) as context:
            ok_(context.active('can drink') is False)
            ok_(context.active('can drink', self.larry) is True)

        with self.inputs(self.manager, self.larry) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink', self.frank, exclusive=True) is False)

    def test_switches_with_multiple_inputs(self):

        with self.inputs(self.manager, self.larry, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('teenager') is False)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

        with self.inputs(self.manager, self.frank, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('teenager') is False)
            ok_(context.active('10 percent') is False)
            ok_(context.active('Upper 50 percent') is True)

    def test_switches_can_concent_top_parent_switch(self):
        with self.inputs(self.manager, self.jeff) as context:
            ok_(context.active('can drink') is True)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('can drink:wine') is True)
        with self.inputs(self.manager, self.timmy) as context:
            ok_(context.active('can drink') is False)
            ok_(context.active('can drink in europe') is True)
            ok_(context.active('SF resident') is True)
            ok_(context.active('can drink:wine') is False)

    def test_changing_parent_is_reflected_in_child_switch(self):
        with self.inputs(self.manager, self.jeff) as context:
            assert self.manager['can drink'].children
            ok_(context.active('can drink:wine') is True)

            parent = self.manager['can drink']
            parent.state = Switch.states.DISABLED
            parent.save()

            assert self.manager['can drink'].children
            ok_(context.active('can drink:wine') is False)


    def test_switches_can_be_deregistered_and_then_autocreated(self):
        with self.inputs(self.manager, self.jeff) as context:
            ok_(context.active('can drink') is True)

            context.manager.unregister('can drink')
            assert_raises(ValueError, context.manager.active, 'can drink')

            context.manager.autocreate = True
            ok_(context.active('can drink') is False)

    def test_can_register_signals_and_get_notified(self):
        signals.switch_registered.connect(self.callback.switch_added)
        signals.switch_unregistered.connect(self.callback.switch_removed)
        signals.switch_updated.connect(self.callback.switch_updated)

        eq_(self.callback.register_calls, [])
        eq_(self.callback.unregister_calls, [])
        eq_(self.callback.update_calls, [])

        switch = Switch('foo')

        self.manager.register(switch)
        eq_(self.callback.register_calls, [switch])

        self.manager.unregister(switch.name)
        eq_(self.callback.unregister_calls, [switch])

        self.manager.register(switch)
        eq_(self.callback.register_calls, [switch, switch])

        switch.name = 'a new name'
        switch.state = Switch.states.GLOBAL
        self.manager.update(switch)

        change = self.callback.update_calls[0]
        eq_(change[0], switch)
        changes = change[1]
        eq_(changes['name'], dict(current='a new name', previous='foo'))
        eq_(changes['state'], dict(current=Switch.states.GLOBAL, previous=Switch.states.DISABLED))

        switch.name = 'from save() call'
        switch.save()

        change = self.callback.update_calls[1]
        eq_(change[0], switch)
        changes = change[1]
        eq_(changes['name'], dict(current='from save() call', previous='a new name'))

    def test_namespaes_keep_switches_isloated(self):
        germany = self.manager.namespaced('germany')
        usa = self.manager.namespaced('usa')

        self.add_switch('booze', condition=self.age_21_plus, manager=usa)
        self.add_switch('booze', condition=self.age_not_under_18, manager=germany)

        eq_(len(germany.switches), 1)
        eq_(len(usa.switches), 1)

        eq_(usa.switches[0].conditions, [self.age_21_plus])
        eq_(germany.switches[0].conditions, [self.age_not_under_18])

        with self.inputs(usa, self.jeff) as context:
            ok_(context.active('booze') is True)

        with self.inputs(usa, self.jeff, self.timmy) as context:
            ok_(context.active('booze') is True)  # Jeff is 21, so he counts
            ok_(context.active('booze', self.timmy, exclusive=True) is False)  # Timmy is 10

        with self.inputs(usa, self.timmy) as context:
            ok_(context.active('booze') is False)

        with self.inputs(usa, self.timmy, self.steve) as context:
            ok_(context.active('booze') is False)

        with self.inputs(germany, self.timmy) as context:
            ok_(context.active('booze') is False)  # 10 is still too young

        with self.inputs(germany, self.steve) as context:
            ok_(context.active('booze') is True)  # 19 is old enough!

        with self.inputs(germany, self.timmy, self.steve) as context:
            ok_(context.active('booze') is True)  # Cause steve is 19

        with self.inputs(germany, self.jeff, self.timmy) as context:
            ok_(context.active('booze') is True)  # Cause jeff is 21

        with self.inputs(germany, self.jeff) as context:
            ok_(context.active('booze', self.timmy, exclusive=True) is False)  # exclusive timmy is 10

    def test_namespace_switches_not_shared_with_parent(self):
        base = self.manager
        daughter = self.manager.namespaced('daughter')
        son = self.manager.namespaced('son')

        ok_(base.switches is not daughter.switches)
        ok_(base.switches is not son.switches)
        ok_(daughter.switches is not son.switches)

        daughter_switch = self.add_switch('daughter only', manager=daughter)
        son_switch = self.add_switch('son only', manager=son)

        eq_(daughter.switches, [daughter_switch])
        eq_(son.switches, [son_switch])

        ok_(daughter_switch not in base.switches)
        ok_(son_switch not in base.switches)

    def test_retrieved_switches_can_be_updated(self):
        switch = Switch('foo')
        self.manager.register(switch)

        switch.name = 'steve'
        switch.save()

        self.assertRaises(ValueError, self.manager.switch, 'foo')
        self.assertEquals(self.manager.switch('steve').name, 'steve')

        switch.name = 'bob'
        switch.state = Switch.states.GLOBAL
        switch.save()

        self.assertEquals(self.manager.switch('bob').name, 'bob')
        self.assertEquals(
            self.manager.switch('bob').state,
            Switch.states.GLOBAL
        )
        self.assertRaises(ValueError, self.manager.switch, 'steve')


class TestIntegrationWithRedis(TestIntegration):

    @fixture
    def redis(self):
        return Redis()

    @before
    def flush_redis(self):
        self.redis.flushdb()

    @fixture
    def manager(self):
        return Manager(storage=RedisDict('gutter-tests', self.redis))

    def test_parent_switch_pickle_input(self):
        import pickle

        # Passing in module `pickle` as unpicklable input.
        evil = User(deterministicstring('evil'), pickle)
        self.manager.input(evil)

        self.manager.autocreate = True

        try:
            self.manager.active('new:switch')
        except pickle.PicklingError, e:
            self.fail('Encountered pickling error: "%s"' % e)
