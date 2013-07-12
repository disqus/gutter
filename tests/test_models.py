import unittest2
import threading
import itertools

from nose.tools import *
from gutter.client.arguments import Container as BaseArgument
from gutter.client import arguments
from gutter.client.models import Switch, Manager, Condition
from durabledict import MemoryDict
from gutter.client import signals
import mock

from exam.decorators import fixture, before
from exam.cases import Exam


def unbound_method():
    pass


class Argument(object):
    def bar(self):
        pass


class MOLArgument(BaseArgument):
    applies = True
    foo = arguments.Value(lambda self: 42)


class TestSwitch(unittest2.TestCase):

    possible_properties = [
        ('name', ('foo', 'bar')),
        ('state', (Switch.states.DISABLED, Switch.states.SELECTIVE)),
        ('compounded', (True, False)),
        ('concent', (True, False))
    ]

    def test_switch_has_state_constants(self):
        self.assertTrue(Switch.states.DISABLED)
        self.assertTrue(Switch.states.SELECTIVE)
        self.assertTrue(Switch.states.GLOBAL)

    def test_no_switch_state_is_equal_to_another(self):
        states = (Switch.states.DISABLED, Switch.states.SELECTIVE,
                  Switch.states.GLOBAL)
        eq_(list(states), list(set(states)))

    def test_switch_constructs_with_a_name_attribute(self):
        eq_(Switch('foo').name, 'foo')

    def test_switch_has_label(self):
        ok_(Switch('foo').label is None)

    def test_switch_can_be_constructed_with_a_label(self):
        eq_(Switch('foo', label='A label').label, 'A label')

    def test_switch_has_description(self):
        ok_(Switch('foo').description is None)

    def test_switch_can_be_constructed_with_a_description(self):
        eq_(Switch('foo', description='A description').description, 'A description')

    def test_switch_strs_the_name_argument(self):
        eq_(Switch(name=12345).name, '12345')

    def test_switch_state_defaults_to_disabled(self):
        eq_(Switch('foo').state, Switch.states.DISABLED)

    def test_switch_state_can_be_changed(self):
        switch = Switch('foo')
        old_state = switch.state

        switch.state = Switch.states.GLOBAL
        eq_(switch.state, Switch.states.GLOBAL)
        ok_(old_state is not switch.state)

    def test_switch_compounded_defaults_to_false(self):
        eq_(Switch('foo').compounded, False)

    def test_swtich_can_be_constructed_with_a_state(self):
        switch = Switch(name='foo', state=Switch.states.GLOBAL)
        eq_(switch.state, Switch.states.GLOBAL)

    def test_swtich_can_be_constructed_with_a_compounded_val(self):
        switch = Switch(name='foo', compounded=True)
        eq_(switch.compounded, True)

    def test_conditions_defaults_to_an_empty_list(self):
        eq_(Switch('foo').conditions, [])

    def test_condtions_can_be_added_and_removed(self):
        switch = Switch('foo')
        condition = lambda: False

        ok_(condition not in switch.conditions)

        switch.conditions.append(condition)
        ok_(condition in switch.conditions)

        switch.conditions.remove(condition)
        ok_(condition not in switch.conditions)

    def test_parent_property_defaults_to_none(self):
        eq_(Switch('foo').parent, None)

    def test_can_be_constructed_with_parent(self):
        eq_(Switch('foo', parent='dog').parent, 'dog')

    def test_concent_defaults_to_true(self):
        eq_(Switch('foo').concent, True)

    def test_can_be_constructed_with_concent(self):
        eq_(Switch('foo', concent=False).concent, False)

    def test_children_defaults_to_an_empty_list(self):
        eq_(Switch('foo').children, [])

    def test_switch_manager_defaults_to_none(self):
        eq_(Switch('foo').manager, None)

    def test_switch_can_be_constructed_witn_a_manager(self):
        eq_(Switch('foo', manager='manager').manager, 'manager')

    @mock.patch('gutter.client.signals.switch_checked')
    def test_switch_enabed_for_calls_switch_checked_signal(self, signal):
        switch = Switch('foo', manager='manager')
        switch.enabled_for(True)
        signal.call.assert_called_once_with(switch)

    @mock.patch('gutter.client.signals.switch_active')
    def test_switch_enabed_for_calls_switch_active_signal_when_enabled(self, signal):
        switch = Switch('foo', manager='manager', state=Switch.states.GLOBAL)
        ok_(switch.enabled_for('causing input'))
        signal.call.assert_called_once_with(switch, 'causing input')

    @mock.patch('gutter.client.signals.switch_active')
    def test_switch_enabed_for_skips_switch_active_signal_when_not_enabled(self, signal):
        switch = Switch('foo', manager='manager', state=Switch.states.DISABLED)
        eq_(switch.enabled_for('causing input'), False)
        eq_(signal.call.called, False)

    def test_switches_are_equal_if_they_have_the_same_properties(self):
        a = Switch('a')
        b = Switch('b')

        for prop, (a_value, b_value) in self.possible_properties:
            setattr(a, prop, a_value)
            setattr(b, prop, b_value)
            self.assertNotEqual(a, b, "expected %s to not be equals" % prop)

            setattr(b, prop, a_value)
            eq_(a, b, "expected %s to be equals" % prop)

    def test_switches_are_still_equal_with_different_managers(self):
        a = Switch('a')
        b = Switch('a')

        eq_(a, b)

        a.manager = 'foo'
        b.manager = 'bar'

        eq_(a, b)


class TestSwitchChanges(unittest2.TestCase):

    @fixture
    def switch(self):
        return Switch('foo')

    def changes_dict(self, previous, current):
        return dict(previous=previous, current=current)

    def test_switch_is_not_changed_by_default(self):
        ok_(Switch('foo').changed is False)

    def test_switch_is_changed_if_property_changes(self):
        ok_(self.switch.changed is False)
        self.switch.name = 'another name'
        ok_(self.switch.changed is True)

    def test_switch_reset_causes_switch_to_reset_change_tracking(self):
        self.switch.name = 'another name'
        ok_(self.switch.changed is True)
        self.switch.reset()
        ok_(self.switch.changed is False)

    def test_switch_changes_returns_changes(self):
        eq_(self.switch.changes, {})

        self.switch.name = 'new name'
        eq_(self.switch.changes, dict(name=self.changes_dict('foo', 'new name')))

        self.switch.concent = False
        eq_(self.switch.changes, dict(
            name=self.changes_dict('foo', 'new name'),
            concent=self.changes_dict(True, False)
        ))


class TestCondition(unittest2.TestCase):

    def argument_dict(name):
        return dict(
            module='module%s' % name,
            klass='klass%s' % name,
            func='func%s' % name
        )

    possible_properties = [
        ('argument_dict', (argument_dict('1'), argument_dict('2'))),
        ('operator', ('o1', 'o2')),
        ('negative', (False, True))
    ]

    @fixture
    def operator(self):
        m = mock.Mock(name='operator')
        m.applies_to.return_value = True
        return m

    @fixture
    def condition(self):
        return Condition(MOLArgument, 'foo', self.operator)

    @fixture
    def input(self):
        return mock.Mock(name='input')

    def test_returns_results_from_calling_operator_with_argument_value(self):
        self.condition.call(self.input)
        self.operator.applies_to.assert_called_once_with(42)

    def test_condition_can_be_negated(self):
        eq_(self.condition.call(self.input), True)
        self.condition.negative = True
        eq_(self.condition.call(self.input), False)

    def test_can_be_negated_via_init_argument(self):
        condition = Condition(MOLArgument, 'foo', self.operator)
        eq_(condition.call(self.input), True)
        condition = Condition(MOLArgument, 'foo', self.operator, negative=True)
        eq_(condition.call(self.input), False)

    def test_if_apply_explodes_it_returns_false(self):
        self.operator.applies_to.side_effect = Exception
        eq_(self.condition.call(self.input), False)

    def test_returns_false_if_argument_does_not_apply_to_input(self):
        self.condition.argument = mock.Mock()
        eq_(self.condition.call(self.input), True)
        self.condition.argument.return_value.applies = False
        eq_(self.condition.call(self.input), False)

    def test_if_input_is_NONE_it_returns_false(self):
        eq_(self.condition.call(Manager.NONE_INPUT), False)

    @mock.patch('gutter.client.signals.condition_apply_error')
    def test_if_apply_explodes_it_signals_condition_apply_error(self, signal):
        error = Exception('boom!')
        inpt = self.input

        self.operator.applies_to.side_effect = error
        self.condition.call(inpt)

        signal.call.assert_called_once_with(self.condition, inpt, error)

    def test_str_returns_argument_and_str_of_operator(self):
        def local_str(self):
            return 'str of operator'

        self.operator.__str__ = local_str
        eq_(str(self.condition), "MOLArgument.foo str of operator")

    def test_equals_if_has_the_same_properties(self):
        a = Condition(Argument, 'bar', bool)
        b = Condition(Argument, 'bar', bool)

        for prop, (a_val, b_val) in self.possible_properties:
            setattr(a, prop, a_val)
            setattr(b, prop, b_val)

            self.assertNotEqual(a, b)

            setattr(b, prop, a_val)
            eq_(a, b)


class SwitchWithConditions(object):

    @fixture
    def switch(self):
        switch = Switch('parent:with conditions', state=Switch.states.SELECTIVE)
        switch.conditions.append(self.pessamistic_condition)
        switch.conditions.append(self.pessamistic_condition)
        return switch

    @fixture
    def parent_switch(self):
        switch = Switch('parent', state=Switch.states.DISABLED)
        return switch

    @property
    def pessamistic_condition(self):
        mck = mock.MagicMock()
        mck.call.return_value = False
        return mck


class ConcentTest(Exam, SwitchWithConditions, unittest2.TestCase):

    @fixture
    def manager(self):
        return Manager(storage=MemoryDict())

    @fixture
    def parent(self):
        p = mock.Mock()
        p.enabled_for.return_value = False
        return p

    @before
    def make_all_conditions_true(self):
        self.make_all_conditions(True)

    @before
    def register_switches(self):
        self.manager.register(self.parent_switch)
        self.manager.register(self.switch)

    def make_all_conditions(self, val):
        for cond in self.switch.conditions:
            cond.call.return_value = val

    def test_with_concent_only_enabled_if_parent_is_too(self):
        self.manager.register(self.switch)

        eq_(self.switch.parent.enabled_for('input'), False)
        eq_(self.manager.active('parent:with conditions', 'input'), False)

        self.switch.parent.state = Switch.states.GLOBAL
        eq_(self.manager.active('parent:with conditions', 'input'), True)

    def test_without_concent_ignores_parents_enabled_status(self):
        self.switch.concent = False
        eq_(self.switch.parent.enabled_for('input'), False)
        eq_(self.switch.enabled_for('input'), True)

        self.make_all_conditions(False)
        eq_(self.switch.enabled_for('input'), False)


class DefaultConditionsTest(SwitchWithConditions, unittest2.TestCase):

    def test_enabled_for_is_true_if_any_conditions_are_true(self):
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[0].call.return_value = True
        ok_(self.switch.enabled_for('input') is True)

    def test_is_true_when_state_is_global(self):
        eq_(self.switch.enabled_for('input'), False)
        self.switch.state = Switch.states.GLOBAL
        eq_(self.switch.enabled_for('input'), True)

    def test_is_false_when_state_is_disabled(self):
        self.switch.conditions[0].call.return_value = True
        eq_(self.switch.enabled_for('input'), True)
        self.switch.state = Switch.states.DISABLED
        eq_(self.switch.enabled_for('input'), False)


class CompoundedConditionsTest(Exam, SwitchWithConditions, unittest2.TestCase):

    @before
    def make_switch_compounded(self):
        self.switch.compounded = True

    def test_enabled_if_all_conditions_are_true(self):
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[0].call.return_value = True
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[1].call.return_value = True
        ok_(self.switch.enabled_for('input') is True)


class ManagerTest(unittest2.TestCase):

    storage_with_existing_switches = {
        'default.existing': 'switch',
        'default.another': 'valuable switch'
    }
    expected_switches_from_storage = ['switch', 'valuable switch']
    namespace_base = []

    @fixture
    def mockstorage(self):
        return mock.MagicMock(dict)

    @fixture
    def manager(self):
        return Manager(storage=self.mockstorage)

    @fixture
    def switch(self):
        switch = mock.Mock(spec=Switch)
        switch.changes = {}
        switch.parent = None
        switch.name = 'foo'
        switch.manager = None
        return switch

    def namespaced(self, *names):
        parts = itertools.chain(self.manager.namespace, names)
        return self.manager.namespace_separator.join(parts)

    def test_autocreate_defaults_to_false(self):
        eq_(Manager(storage=dict()).autocreate, False)

    def test_autocreate_can_be_passed_to_init(self):
        eq_(Manager(storage=dict(), autocreate=True).autocreate, True)

    def test_namespace_defaults_to_default(self):
        eq_(Manager(storage=dict()).namespace, ['default'])

    def test_namespace_can_be_set_on_construction(self):
        eq_(Manager(storage=dict(), namespace='foo').namespace, ['foo'])

    def test_register_adds_switch_to_storge_keyed_by_its_name(self):
        self.manager.register(self.switch)
        self.mockstorage.__setitem__.assert_called_once_with(
            self.namespaced(self.switch.name),
            self.switch
        )

    def test_register_adds_self_as_manager_to_switch(self):
        ok_(self.switch.manager is not self.manager)
        self.manager.register(self.switch)
        ok_(self.switch.manager is self.manager)

    def test_register_adds_switch_to_storage_before_setting_manager(self):
        def assert_no_manger(key, switch):
            ok_(switch.manager is None)

        self.switch.manager = True
        self.mockstorage.__setitem__.side_effect = assert_no_manger
        self.manager.register(self.switch)

    def test_uses_switches_from_storage_on_itialization(self):
        self.manager.storage = self.storage_with_existing_switches
        self.assertItemsEqual(
            self.manager.switches,
            self.expected_switches_from_storage
        )

    def test_update_tells_manager_to_register_with_switch_updated_signal(self):
        self.manager.register = mock.Mock()
        self.manager.update(self.switch)
        self.manager.register.assert_called_once_with(self.switch, signal=signals.switch_updated)

    @mock.patch('gutter.client.signals.switch_updated')
    def test_update_calls_the_switch_updateed_signal(self, signal):
        self.manager.update(self.switch)
        signal.call.assert_call_once()

    def test_manager_resets_switch_dirty_tracking(self):
        self.manager.update(self.switch)
        self.switch.reset.assert_called_once_with()

    def test_manager_properties_not_shared_between_threads(self):
        manager = Manager(storage=self.mockstorage, autocreate=True)

        def change_autocreate_to_false():
            manager.autocreate = False

        threading.Thread(target=change_autocreate_to_false).start()
        eq_(manager.autocreate, True)

    def test_can_be_constructed_with_inputs(self):
        eq_(
            Manager(storage=self.mockstorage, inputs=[3]).inputs,
            [3]
        )

    def test_namespaced_returns_new_manager_only_different_by_namespace(self):
        parent = self.manager
        child = self.manager.namespaced('ns')
        grandchild = child.namespaced('other')

        self.assertNotEqual(parent.namespace, child.namespace)
        self.assertNotEqual(child.namespace, grandchild.namespace)

        child_ns_list = list(itertools.chain(self.namespace_base, ['ns']))
        grandchild_ns_list = list(
            itertools.chain(self.namespace_base, ['ns', 'other'])
        )

        eq_(child.namespace, child_ns_list)
        eq_(grandchild.namespace, grandchild_ns_list)

        properties = (
            'storage',
            'autocreate',
            'inputs',
            'switch_class'
        )

        for decendent_manager in (child, grandchild):
            for prop in properties:
                eq_(getattr(decendent_manager, prop), getattr(parent, prop))

    def test_getitem_proxies_to_storage_getitem(self):
        eq_(
            self.manager['foo'],
            self.manager.storage.__getitem__.return_value
        )
        self.manager.storage.__getitem__.assert_called_once_with(
            self.namespaced('foo')
        )


class NamespacedManagertest(ManagerTest):

    storage_with_existing_switches = {
        'a.b.brother': 'brother switch',
        'a.b.sister': 'sister switch',
        'a.b.c.grandchild': 'grandchild switch',
        'a.c.cousin': 'cousin switch',
    }
    expected_switches_from_storage = [
        'brother switch',
        'sister switch',
        'grandchild switch'
    ]
    namespace_base = ['a', 'b']

    @fixture
    def manager(self):
        return Manager(storage=self.mockstorage, namespace=['a', 'b'])


class ActsLikeManager(object):

    def namespaced(self, *names):
        parts = itertools.chain(self.manager.namespace, names)
        return self.manager.key_separator.join(parts)

    @fixture
    def manager(self):
        return Manager(storage=MemoryDict())

    @fixture
    def test_switch(self):
        return self.new_switch('test')

    def new_switch(self, name, parent=None):
        switch = mock.Mock(name=name)
        switch.name = name
        switch.parent = parent
        switch.children = []
        return switch

    def mock_and_register_switch(self, name, parent=None):
        switch = self.new_switch(name, parent)
        self.manager.register(switch)
        return switch

    def test_switches_list_registed_switches(self):
        eq_(self.manager.switches, [])
        self.manager.register(self.test_switch)
        eq_(self.manager.switches, [self.test_switch])

    def test_active_raises_exception_if_no_switch_found_with_name(self):
        assert_raises(ValueError, self.manager.active, 'junk')

    def test_unregister_removes_a_switch_from_storage_with_name(self):
        switch = self.mock_and_register_switch('foo')
        ok_(switch in self.manager.switches)

        self.manager.unregister(switch.name)
        ok_(switch not in self.manager.switches)

    def test_unregister_can_remove_if_given_switch_instance(self):
        switch = self.mock_and_register_switch('foo')
        ok_(switch in self.manager.switches)

        self.manager.unregister(switch)
        ok_(switch not in self.manager.switches)

    def test_register_does_not_set_parent_by_default(self):
        switch = self.mock_and_register_switch('foo')
        eq_(switch.parent, None)

    def test_register_sets_parent_on_switch_if_there_is_one(self):
        parent = self.mock_and_register_switch('movies')
        child = self.mock_and_register_switch('movies:jaws')
        eq_(child.parent, parent)

    def test_register_adds_self_to_parents_children(self):
        parent = self.mock_and_register_switch('movies')
        child = self.mock_and_register_switch('movies:jaws')

        eq_(parent.children, [child])

        sibling = self.mock_and_register_switch('movies:jaws')

        eq_(parent.children, [child, sibling])

    def test_register_removes_switch_from_children_of_old_parent(self):
        parent = self.mock_and_register_switch('movies')
        child = self.mock_and_register_switch('movies:jaws')
        foster_parent = self.mock_and_register_switch('books')

        ok_(child in parent.children)
        ok_(child not in foster_parent.children)
        ok_(child.parent is parent)

        child.name = 'books:jaws'
        self.manager.register(child)

        ok_(child not in parent.children)
        ok_(child in foster_parent.children)
        ok_(child.parent is foster_parent)

    def test_register_raises_value_error_for_blank_name(self):
        with self.assertRaises(ValueError):
            self.mock_and_register_switch('')

    def test_switch_returns_switch_from_manager_with_name(self):
        switch = self.mock_and_register_switch('foo')
        eq_(switch, self.manager.switch('foo'))

    def test_switch_returns_switch_with_manager_assigned(self):
        switch = self.new_switch('foo')
        self.manager.register(switch)
        switch.manager = None
        eq_(self.manager, self.manager.switch('foo').manager)

    def test_swich_raises_valueerror_if_no_switch_by_name(self):
        assert_raises(ValueError, self.manager.switch, 'junk')

    def test_unregister_removes_all_child_switches_too(self):
        grandparent = self.mock_and_register_switch('movies')
        parent = self.mock_and_register_switch('movies:star_wars')
        child1 = self.mock_and_register_switch('movies:star_wars:a_new_hope')
        child2 = self.mock_and_register_switch('movies:star_wars:return_of_the_jedi')
        great_uncle = self.mock_and_register_switch('books')

        ok_(grandparent in self.manager.switches)
        ok_(parent in self.manager.switches)
        ok_(child1 in self.manager.switches)
        ok_(child2 in self.manager.switches)
        ok_(great_uncle in self.manager.switches)

        self.manager.unregister(grandparent.name)

        ok_(grandparent not in self.manager.switches)
        ok_(parent not in self.manager.switches)
        ok_(child1 not in self.manager.switches)
        ok_(child2 not in self.manager.switches)
        ok_(great_uncle in self.manager.switches)

    @mock.patch('gutter.client.signals.switch_unregistered')
    def test_register_signals_switch_registered_with_switch(self, signal):
        switch = self.mock_and_register_switch('foo')
        self.manager.unregister(switch.name)
        signal.call.assert_called_once_with(switch)

    def test_update_does_not_linger_old_switch(self):
        switch = self.mock_and_register_switch('foo')
        switch.name = 'new name'
        switch.changes = dict(name=dict(previous='foo'))

        ok_(self.manager.switch('foo'))
        assert_raises(ValueError, self.manager.switch, 'new name')
        self.manager.update(switch)
        assert_raises(ValueError, self.manager.switch, 'foo')
        ok_(self.manager.switch('new name'))


class EmptyManagerInstanceTest(ActsLikeManager, unittest2.TestCase):

    def test_input_accepts_variable_input_args(self):
        eq_(self.manager.inputs, [])
        self.manager.input('input1', 'input2')
        eq_(self.manager.inputs, ['input1', 'input2'])

    def test_flush_clears_all_inputs(self):
        self.manager.input('input1', 'input2')
        ok_(len(self.manager.inputs) is 2)
        self.manager.flush()
        ok_(len(self.manager.inputs) is 0)

    def test_can_pass_extra_inputs_to_check_enabled_for_on(self):
        switch = self.mock_and_register_switch('foo')
        additional_input = mock.Mock()
        self.manager.active('foo', additional_input)
        switch.enabled_for.assert_called_once_with(additional_input)

    def test_checks_against_NONE_input_if_no_inputs(self):
        switch = self.mock_and_register_switch('global')
        eq_(self.manager.inputs, [])

        self.manager.active('global')

        switch.enabled_for.assert_called_once_with(Manager.NONE_INPUT)


class NamespacedEmptyManagerInstanceTest(EmptyManagerInstanceTest):

    @fixture
    def manager(self):
        return Manager(storage=MemoryDict(), namespace=['a', 'b'])


class ManagerWithInputTest(Exam, ActsLikeManager, unittest2.TestCase):

    def build_and_register_switch(self, name, enabled_for=False):
        switch = Switch(name)
        switch.enabled_for = mock.Mock(return_value=enabled_for)
        self.manager.register(switch)
        return switch

    @before
    def add_to_inputs(self):
        self.manager.input('input 1', 'input 2')

    def test_returns_boolean_if_named_switch_is_enabled_for_any_input(self):
        self.build_and_register_switch('disabled', enabled_for=False)
        eq_(self.manager.active('disabled'), False)

        self.build_and_register_switch('enabled', enabled_for=True)
        eq_(self.manager.active('disabled'), False)

    def test_raises_exception_if_invalid_switch_name_created(self):
        self.assertRaisesRegexp(ValueError, 'switch named', self.manager.active, 'junk')

    def test_autocreates_disabled_switch_when_autocreate_is_true(self):
        eq_(self.manager.switches, [])
        assert_raises(ValueError, self.manager.active, 'junk')

        self.manager.autocreate = True

        eq_(self.manager.active('junk'), False)
        ok_(len(self.manager.switches) is 1)
        ok_(self.manager.switches[0].state, Switch.states.DISABLED)

    def test_active_extra_inputs_considered_in_check_with_global_inputs(self):
        switch = self.build_and_register_switch('foo')
        self.manager.active('foo', 'input 3')
        calls = [mock.call(c) for c in ('input 1', 'input 2', 'input 3')]
        switch.enabled_for.assert_has_calls(calls)

    def test_active_with_extra_inputs_only_considers_extra_when_only_kw_arg_is_used(self):
        switch = self.build_and_register_switch('foo')
        self.manager.active('foo', 'input 3', exclusive=True)
        switch.enabled_for.assert_called_once_with('input 3')


class NamespacedManagerWithInputTest(ManagerWithInputTest):

    @fixture
    def manager(self):
        return Manager(storage=MemoryDict(), namespace=['a', 'b'])
