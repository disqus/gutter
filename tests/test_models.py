import unittest
import threading
from nose.tools import *
from gargoyle.client.models import Switch, Manager, Condition
from modeldict.dict import MemoryDict
from gargoyle.client import signals
from tests import fixture
import mock


switch = Switch('test')


def unbound_method():
    pass


class Argument(object):
    def bar(self):
        pass


class ReflectiveInput(object):
    def foo(self):
        return (42, self)


class TestSwitch(unittest.TestCase):

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

    @mock.patch('gargoyle.client.signals.switch_checked')
    def test_switch_enabed_for_calls_switch_checked_signal(self, signal):
        switch = Switch('foo', manager='manager')
        switch.enabled_for(True)
        signal.call.assert_called_once_with(switch)

    @mock.patch('gargoyle.client.signals.switch_active')
    def test_switch_enabed_for_calls_switch_active_signal_when_enabled(self, signal):
        switch = Switch('foo', manager='manager', state=Switch.states.GLOBAL)
        ok_(switch.enabled_for('causing input'))
        signal.call.assert_called_once_with(switch, 'causing input')

    @mock.patch('gargoyle.client.signals.switch_active')
    def test_switch_enabed_for_skips_switch_active_signal_when_not_enabled(self, signal):
        switch = Switch('foo', manager='manager', state=Switch.states.DISABLED)
        eq_(switch.enabled_for('causing input'), False)
        eq_(signal.call.called, False)


class TestSwitchChanges(unittest.TestCase):

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


class TestCondition(unittest.TestCase):

    def setUp(self):
        self.operator = mock.Mock(name='operator')
        self.operator.applies_to.return_value = True
        self.condition = Condition(ReflectiveInput.foo, self.operator)

    def test_raises_valueerror_if_argument_not_callable(self):
        assert_raises_regexp(ValueError, 'must be callable', Condition,
                             True, self.operator)

    def test_raises_value_error_if_argument_has_arity_of_0(self):
        assert_raises_regexp(ValueError, 'must have an arity > 0', Condition,
                             unbound_method, self.operator)

    def test_returns_false_if_input_is_not_same_class_as_argument_class(self):
        eq_(self.condition.call(object()), False)

    def test_returns_results_from_calling_operator_with_argument_value(self):
        """
        This test verifies that when a condition is called with an instance of
        an Input as the argument, the vaue that the condition's operator is
        asked if it applies to is calculated by calling the condition's own
        argument function as bound to the instance of the Input originally
        passed to the condition.

        By using the ReflectiveInput class, we can verify that it was called
        with expected arguments, which are returned in a tuple with an extra
        value (42), and that that tuple is passed to the operator's applied_to
        method.
        """

        input_instance = ReflectiveInput()
        self.condition.call(input_instance)
        self.operator.applies_to.assert_called_once_with((42, input_instance))

    def test_condition_can_be_negated(self):
        eq_(self.condition.call(ReflectiveInput()), True)
        self.condition.negative = True
        eq_(self.condition.call(ReflectiveInput()), False)

    def test_can_be_negated_via_init_argument(self):
        condition = Condition(ReflectiveInput.foo, self.operator)
        eq_(condition.call(ReflectiveInput()), True)
        condition = Condition(ReflectiveInput.foo, self.operator, negative=True)
        eq_(condition.call(ReflectiveInput()), False)

    def test_if_apply_explodes_it_returns_false(self):
        self.operator.applies_to.side_effect = Exception
        eq_(self.condition.call(ReflectiveInput()), False)

    @mock.patch('gargoyle.client.signals.condition_apply_error')
    def test_if_apply_explodes_it_signals_condition_apply_error(self, signal):
        error = Exception('boom!')
        inpt = ReflectiveInput()

        self.operator.applies_to.side_effect = error
        self.condition.call(inpt)

        signal.call.assert_called_once_with(self.condition, inpt, error)

    def test_str_returns_argument_and_str_of_operator(self):
        def local_str(self):
            return 'str of operator'

        self.operator.__str__ = local_str
        eq_(str(self.condition), "ReflectiveInput.foo str of operator")

    def test_can_pickle_instancemethods(self):
        import pickle
        condition = Condition(Argument.bar, bool)

        string = pickle.dumps(condition)
        rebuilt = pickle.loads(string)
        eq_(rebuilt.operator, condition.operator)
        eq_(rebuilt.argument, condition.argument)


class SwitchWithConditions(object):

    def setUp(self):
        self.switch = Switch('with conditions', state=Switch.states.SELECTIVE)
        self.switch.conditions.append(self.pessamistic_condition)
        self.switch.conditions.append(self.pessamistic_condition)

    @property
    def pessamistic_condition(self):
        mck = mock.MagicMock()
        mck.call.return_value = False
        return mck


class ConcentTest(SwitchWithConditions, unittest.TestCase):

    def setUp(self):
        super(ConcentTest, self).setUp()
        self.parent = mock.Mock()
        self.parent.enabled_for.return_value = False
        self.switch.parent = self.parent
        self.make_all_conditions(True)

    def make_all_conditions(self, val):
        for cond in self.switch.conditions:
            cond.call.return_value = val

    def test_with_concent_only_enabled_if_parent_is_too(self):
        eq_(self.switch.parent.enabled_for('input'), False)
        eq_(self.switch.enabled_for('input'), False)

        self.switch.parent.enabled_for.return_value = True
        eq_(self.switch.enabled_for('input'), True)

    def test_without_concent_ignores_parents_enabled_status(self):
        self.switch.concent = False
        eq_(self.switch.parent.enabled_for('input'), False)
        eq_(self.switch.enabled_for('input'), True)

        self.make_all_conditions(False)
        eq_(self.switch.enabled_for('input'), False)


class DefaultConditionsTest(SwitchWithConditions, unittest.TestCase):

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


class CompoundedConditionsTest(SwitchWithConditions, unittest.TestCase):

    def setUp(self):
        super(CompoundedConditionsTest, self).setUp()
        self.switch.compounded = True

    def test_enabled_if_all_conditions_are_true(self):
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[0].call.return_value = True
        ok_(self.switch.enabled_for('input') is False)
        self.switch.conditions[1].call.return_value = True
        ok_(self.switch.enabled_for('input') is True)


class ManagerTest(unittest.TestCase):

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

    def test_autocreate_defaults_to_false(self):
        eq_(Manager(storage=dict()).autocreate, False)

    def test_autocreate_can_be_passed_to_init(self):
        eq_(Manager(storage=dict(), autocreate=True).autocreate, True)

    def test_register_adds_switch_to_storge_keyed_by_its_name(self):
        self.manager.register(switch)
        self.mockstorage.__setitem__.assert_called_once_with(switch.name, switch)

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
        m = Manager(storage=dict(existing='switch', another='valuable switch'))
        self.assertItemsEqual(m.switches, ['switch', 'valuable switch'])

    def test_update_tells_manager_to_register_with_switch_updated_signal(self):
        self.manager.register = mock.Mock()
        self.manager.update(self.switch)
        self.manager.register.assert_called_once_with(self.switch, signal=signals.switch_updated)

    @mock.patch('gargoyle.client.signals.switch_updated')
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

    def test_has_operators_that_can_be_appended(self):
        eq_(self.manager.operators, [])


class ActsLikeManager(object):

    def setUp(self):
        self.manager = Manager(storage=MemoryDict())

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
        self.manager.register(switch)
        eq_(self.manager.switches, [switch])

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

    @mock.patch('gargoyle.client.signals.switch_unregistered')
    def test_register_signals_switch_registered_with_switch(self, signal):
        switch = self.mock_and_register_switch('foo')
        self.manager.unregister(switch.name)
        signal.call.assert_called_once_with(switch)

    def test_update_does_not_linger_old_switch(self):
        switch = self.mock_and_register_switch('foo')
        switch.name = 'new name'
        switch.changes = dict(name=dict(previous='foo'))

        ok_(self.manager.switch('foo'))
        assert_raises(ValueError, self.manager.switch, ' new name')
        self.manager.update(switch)
        assert_raises(ValueError, self.manager.switch, 'foo')
        ok_(self.manager.switch('new name'))


class EmptyManagerInstanceTest(ActsLikeManager, unittest.TestCase):

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


class ManagerWithInputTest(ActsLikeManager, unittest.TestCase):

    def build_and_register_switch(self, name, enabled_for=False):
        switch = Switch(name)
        switch.enabled_for = mock.Mock(return_value=enabled_for)
        self.manager.register(switch)
        return switch

    def setUp(self):
        super(ManagerWithInputTest, self).setUp()
        self.manager.input('input 1', 'input 2')

    def test_returns_boolean_if_named_switch_is_enabled_for_any_input(self):
        self.build_and_register_switch('disabled', enabled_for=False)
        eq_(self.manager.active('disabled'), False)

        self.build_and_register_switch('enabled', enabled_for=True)
        eq_(self.manager.active('disabled'), False)

    def test_raises_exception_if_invalid_switch_name_created(self):
        assert_raises_regexp(ValueError, 'switch named', self.manager.active, 'junk')

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
