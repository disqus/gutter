"""
gutter.models
~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import absolute_import

# Standard Library
import threading
from collections import defaultdict
from functools import partial

# External Libraries
import six
from gutter.client import signals
from gutter.client.compat import ifilter

DEFAULT_SEPARATOR = ':'


def all_false_if_empty(iterable):
    if not iterable:
        return False

    for element in iterable:
        if not element:
            return False
    return True


class ConditionsDict(defaultdict):

    @classmethod
    def from_conditions_list(cls, conditions):
        conditions_dict = cls(set)

        for cond in conditions:
            conditions_dict[cond.argument.COMPATIBLE_TYPE].add(cond)

        return conditions_dict

    def get_by_input(self, inpt):
        return self.get_by_type(type(inpt))

    def get_by_type(self, to_get_key):
        if to_get_key in self:
            return self[to_get_key]
        for key_type in self:
            if issubclass(to_get_key, key_type):
                return self[key_type]

        # raise the correct exception
        return self[to_get_key]


class Switch(object):

    """
    A switch encapsulates the concept of an item that is either 'on' or 'off'
    depending on the input.  The switch determines this by checking each of its
    conditions and seeing if it applies to a certain input.  All the switch does
    is ask each of its Conditions if it applies to the provided input.  Normally
    any condition can be true for the Switch to be enabled for a particular
    input, but of ``switch.compounded`` is set to True, then **all** of the
    switches conditions need to be true in order to be enabled.

    See the Condition class for more information on what a Condition is and how
    it checks to see if it's satisfied by an input.
    """

    class states:
        DISABLED = 1
        SELECTIVE = 2
        GLOBAL = 3

    def __init__(
            self,
            name,
            state=states.DISABLED,
            compounded=False,
            concent=True,
            manager=None,
            label=None,
            description=None,
            **kwargs
    ):
        self._name = str(name)
        self.label = label
        self.description = description
        self.state = state
        self.conditions = []
        self.compounded = compounded
        self.concent = concent
        self.manager = manager
        self.reset()

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        separator = getattr(self.manager, 'key_separator', DEFAULT_SEPARATOR)
        parent = self.name.rsplit(separator, 1)[0]
        return parent if parent != self.name else None

    def get_parent(self):
        return self.manager.switch(self.parent) if self.parent else None

    def __repr__(self):
        kwargs = dict(
            state=self.state,
            compounded=self.compounded,
            concent=self.concent
        )
        parts = ["%s=%s" % (k, v) for k, v in kwargs.items()]
        return '<Switch("%s") conditions=%s, %s>' % (
            self.name,
            len(self.conditions),
            ', '.join(parts)
        )

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.state is other.state and
            self.compounded is other.compounded and
            self.concent is other.concent
        )

    def __getstate__(self):
        inner_dict = vars(self).copy()
        inner_dict.pop('manager', False)
        return inner_dict

    def __setstate__(self, state):
        # remove parent from the state, this is now a calculated field
        for attr in (
            'parent',
            'children',
        ):
            state.pop(attr, '')

        self.__dict__ = state
        if not hasattr(self, 'manager'):
            setattr(self, 'manager', None)

    def enabled_for(self, inpt):
        """
        Checks to see if this switch is enabled for the provided input.

        If ``compounded``, all switch conditions must be ``True`` for the switch
        to be enabled.  Otherwise, *any* condition needs to be ``True`` for the
        switch to be enabled.

        The switch state is then checked to see if it is ``GLOBAL`` or
        ``DISABLED``.  If it is not, then the switch is ``SELECTIVE`` and each
        condition is checked.

        Keyword Arguments:
        inpt -- An instance of the ``Input`` class.
        """

        signals.switch_checked.call(self)
        signal_decorated = partial(self.__signal_and_return, inpt)

        if self.state is self.states.GLOBAL:
            return signal_decorated(True)
        elif self.state is self.states.DISABLED:
            return signal_decorated(False)

        conditions_dict = ConditionsDict.from_conditions_list(self.conditions)
        conditions = conditions_dict.get_by_input(inpt)

        if conditions:
            result = self.__enabled_func(
                cond.call(inpt)
                for cond
                in conditions
                if cond.argument(inpt).applies
            )
        else:
            result = None

        return signal_decorated(result)

    def enabled_for_all(self, *inpts):
        foo = ifilter(
            lambda x: x is not None,
            (self.enabled_for(inpt) for inpt in inpts)
        )
        return self.__enabled_func(foo)

    def save(self):
        """
        Saves this switch in its manager (if present).

        Equivalent to ``self.manager.update(self)``.  If no ``manager`` is set
        for the switch, this method is a no-op.
        """
        if self.manager:
            self.manager.update(self)

    @property
    def changes(self):
        """
        A dictionary of changes to the switch since last saved.

        Switch changes are a dict in the following format::

            {
                'property_name': {'previous': value, 'current': value}
            }

        For example, if the switch name change from ``foo`` to ``bar``, the
        changes dict will be in the following structure::

            {
                'name': {'previous': 'foo', 'current': 'bar'}
            }
        """
        return dict(list(self.__changes()))

    @property
    def changed(self):
        """
        Boolean of if the switch has changed since last saved.
        """
        return bool(list(self.__changes()))

    def reset(self):
        """
        Resets switch change tracking.

        No switch properties are altered, only the tracking of what has changed
        is reset.
        """
        self.__init_vars = vars(self).copy()

    @property
    def state_string(self):
        state_vars = vars(self.states)
        rev = dict(zip(state_vars.values(), state_vars))
        return rev[self.state]

    @property
    def __enabled_func(self):
        if self.compounded:
            return all_false_if_empty
        else:
            return any

    def __changes(self):
        for key, value in self.__init_vars.items():
            if key is '_Switch__init_vars':
                continue
            elif key not in vars(self) or getattr(self, key) != value:
                yield (key, dict(previous=value, current=getattr(self, key)))

    def __signal_and_return(self, inpt, is_enabled):
        if is_enabled:
            signals.switch_active.call(self, inpt)

        return is_enabled


class Condition(object):

    """
    A Condition is the configuration of an argument, its attribute and an
    operator. It tells you if it itself is true or false given an input.

    The ``argument`` defines what this condition is checking.  Perhaps it's a
    ``User`` or ``Request`` object. The ``attribute`` name is then extracted out
    of an instance of the argument to produce a variable. That variable is then
    compared to the operator to determine if the condition applies to the input
    or not.

    For example, for the request IP address, you would define a ``Request``
    argument, that had an ``ip`` property.  A condition would then be constructed
    like so:

    from myapp.gutter import RequestArgument
    from gutter.client.models import Condition

        >> condition = Condition(argument=RequestArgument, attribute='ip', operator=some_operator)

    When the Condition is called, it is passed the input. The argument is then
    called (constructed) with input object to produce an instance.  The
    attribute is then extracted from that instance to produce the variable.
    The extracted variable is then checked against the operator.

    To put it another way, say you wanted a condition to only allow your switch
    to people between 15 and 30 years old.  To make the condition:

        1. You would create a ``UserArgument`` class that takes a user object in
           its constructor.  The class also has an ``age`` method which returns
           the user object's age.
        2. You would then create a new Condition via:
           ``Condition(argument=UserInput, attribute='age', operator=Between(15, 30))``.
        3. You then call that condition with a ``User``, and it would return
           ``True`` if the age of the user the ``UserArgument`` instance wraps
           is between 15 and 30.
    """

    def __init__(self, argument, attribute, operator, negative=False):
        self.attribute = attribute
        self.argument = argument
        self.operator = operator
        self.negative = negative

    @property
    def __is_or_is_not(self):
        return 'is not' if self.negative else 'is'

    def __repr__(self):
        argument = ".".join((self.argument.__name__, self.attribute))
        return '<Condition "%s" %s %s>' % (argument, self.__is_or_is_not, self.operator)

    def __str__(self):
        return "%s %s %s" % (self.argument_string, self.__is_or_is_not, self.operator)

    def __eq__(self, other):
        return (
            self.argument == other.argument and
            self.attribute == other.attribute and
            self.operator == other.operator and
            self.negative is other.negative
        )

    # TODO: not sure if that's ok
    __hash__ = object.__hash__

    def call(self, inpt):
        """
        Returns if the condition applies to the ``inpt``.

        If the class ``inpt`` is an instance of is not the same class as the
        condition's own ``argument``, then ``False`` is returned.  This also
        applies to the ``NONE`` input.

        Otherwise, ``argument`` is called, with ``inpt`` as the instance and
        the value is compared to the ``operator`` and the Value is returned.  If
        the condition is ``negative``, then then ``not`` the value is returned.

        Keyword Arguments:
        inpt -- An instance of the ``Input`` class.
        """
        if inpt is Manager.NONE_INPUT:
            return False

        # Call (construct) the argument with the input object
        argument_instance = self.argument(inpt)

        if not argument_instance.applies:
            return False

        application = self.__apply(argument_instance, inpt)

        if self.negative:
            application = not application

        return application

    @property
    def argument_string(self):
        parts = [self.argument.__name__, self.attribute]
        return '.'.join(map(str, parts))

    def __apply(self, argument_instance, inpt):
        variable = getattr(argument_instance, self.attribute)

        try:
            return self.operator.applies_to(variable)
        except Exception as error:
            signals.condition_apply_error.call(self, inpt, error)
            return False


class Manager(threading.local):

    """
    The Manager holds all state for Gutter.  It knows what Switches have been
    registered, and also what Input objects are currently being applied.  It
    also offers an ``active`` method to ask it if a given switch name is
    active, given its conditions and current inputs.
    """

    key_separator = DEFAULT_SEPARATOR
    namespace_separator = '.'
    default_namespace = ['default']

    #: Special singleton used to represent a "no input" which arguments can look
    #: for and ignore
    NONE_INPUT = object()

    def __init__(
        self,
        storage=None,
        autocreate=False,
        switch_class=Switch,
        inputs=None,
        namespace=None
    ):
        if storage is None:
            # todo: make a better check
            raise TypeError('storage must be a dict like value')

        if inputs is None:
            inputs = []

        if namespace is None:
            namespace = self.default_namespace
        elif isinstance(namespace, six.string_types):
            namespace = [namespace]

        self.storage = storage
        self.autocreate = autocreate
        self.inputs = inputs
        self.switch_class = switch_class
        self.namespace = namespace

    def __getstate__(self):
        inner_dict = vars(self).copy()
        inner_dict.pop('inputs', False)
        inner_dict.pop('storage', False)
        return inner_dict

    def __getitem__(self, key):
        return self.switch(key)

    def __contains__(self, key):
        return self.__namespaced(key) in self.storage

    def __delitem__(self, key):
        del self.storage[self.__namespaced(key)]

    @property
    def switches(self):
        """
        List of all switches currently registered.
        """
        results = [
            switch for name, switch in six.iteritems(self.storage)
            if name.startswith(self.__joined_namespace)
        ]

        return results

    def switch(self, name):
        """
        Returns the switch with the provided ``name``.

        If ``autocreate`` is set to ``True`` and no switch with that name
        exists, a ``DISABLED`` switch will be with that name.

        Keyword Arguments:
        name -- A name of a switch.
        """
        try:
            switch = self.storage[self.__namespaced(name)]
        except KeyError:
            if not self.autocreate:
                raise ValueError("No switch named '%s' registered in '%s'" % (name, self.namespace))

            switch = self.__create_and_register_disabled_switch(name)

        switch.manager = self
        return switch

    def get_children(self, parent):
        namespaced_parent = self.__namespaced(parent) + ':'
        return [
            self.__denamespaced(child)
            for child
            in self.storage.keys()
            if child.startswith(namespaced_parent)
        ]

    def register(self, switch, signal=signals.switch_registered):
        '''
        Register a switch and persist it to the storage.
        '''
        if not switch.name:
            raise ValueError('Switch name cannot be blank')

        switch.manager = self
        self.__persist(switch)

        signal.call(switch)

    def unregister(self, switch_or_name):
        switch = getattr(switch_or_name, 'name', switch_or_name)

        for child in self.get_children(switch):
            self.unregister(child)

        if switch in self:
            signals.switch_unregistered.call(self.switch(switch))
            del self.storage[self.__namespaced(switch)]

    def input(self, *inputs):
        self.inputs = list(inputs)

    def flush(self):
        self.inputs = []

    def active(self, name, *inputs, **kwargs):
        switch = self.switch(name)

        if not kwargs.get('exclusive', False):
            inputs = tuple(self.inputs) + inputs

        # Also check the switches against "NONE" input. This ensures there will
        # be at least one input checked.
        if not inputs:
            inputs = (self.NONE_INPUT,)

        # If necessary, the switch first consents with its parent and returns
        # false if the switch is consenting and the parent is not enabled for
        # ``inputs``.

        if (
            switch.concent
            and switch.get_parent()
            and not self.active(switch.parent, *inputs, **kwargs)
        ):
            return False

        return switch.enabled_for_all(*inputs)

    def update(self, switch):

        self.register(switch, signal=signals.switch_updated)
        switch.reset()

    def namespaced(self, namespace):
        new_namespace = []

        # Only start with the current namesapce if it's not the default
        # namespace
        if self.namespace is not self.default_namespace:
            new_namespace = list(self.namespace)

        new_namespace.append(namespace)

        return type(self)(
            storage=self.storage,
            autocreate=self.autocreate,
            inputs=self.inputs,
            switch_class=self.switch_class,
            namespace=new_namespace,
        )

    def __persist(self, switch):
        self.storage[self.__namespaced(switch.name)] = switch
        return switch

    def __create_and_register_disabled_switch(self, name):
        switch = self.switch_class(name)
        switch.state = self.switch_class.states.DISABLED
        self.register(switch)
        return switch

    def __parent_key_for(self, switch):
        # TODO: Make this a method on the switch object
        return self.name.rsplit(self.key_separator, 1)[:-1]
        # parent_parts = switch.name.split(self.key_separator)[:-1]
        # return self.key_separator.join(parent_parts)

    def __namespaced(self, name=''):
        if not self.__joined_namespace:
            return name
        else:
            return self.namespace_separator.join(
                (self.__joined_namespace, name)
            )

    def __denamespaced(self, name=''):
        prefix = self.__joined_namespace + self.namespace_separator
        if prefix and name.startswith(prefix):
            return name.replace(prefix, '', 1)
        return name

    @property
    def __joined_namespace(self):
        return self.namespace_separator.join(self.namespace)
