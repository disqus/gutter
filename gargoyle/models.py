"""
gargoyle.models
~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from gargoyle import signals


class Switch(object):
    """
    A switch encapsulates the concept of an item that is either 'on' or 'off'
    depending on the input.  The swich determines this by checking each of its
    conditions and seeing if it applies to a certain input.  All the switch does
    is ask each of its Conditions if it applies to the provided input.  Normally
    any condition can be true for the Switch to be enabled for a particular
    input, but of ``switch.componded`` is set to True, then **all** of the
    switches conditions need to be true in order to be enabled.

    See the Condition class for more information on what a Condition is and how
    it checks to see if it's satisfied by an input.
    """

    class ConditionList(list):

        def __init__(self, switch, *args, **kwargs):
            self.switch = switch
            super(Switch.ConditionList, self).__init__(*args, **kwargs)

        # TODO: support other ways to append items from a list?
        def append(self, item):
            super(Switch.ConditionList, self).append(item)
            signals.switch_condition_added.call(self.switch, item)

        # TODO: support other ways to remove items from a list?
        def remove(self, item):
            super(Switch.ConditionList, self).remove(item)
            signals.switch_condition_removed.call(self.switch, item)


    class states:
        DISABLED = 1
        SELECTIVE = 2
        GLOBAL = 3

    def __init__(self, name, state=states.DISABLED, compounded=False,
                 parent=None, concent=True, manager=None):
        self.name = str(name)
        self.state = state
        self.conditions = self.ConditionList(switch=self)
        self.compounded = compounded
        self.parent = parent
        self.concent = concent
        self.children = []
        self.manager = manager
        self.reset()

    def enabled_for(self, inpt):
        """
        Checks to see if this switch is enabled for the provided input, which is
        an instance of the ``Input`` class.  The switch is enabled if any of its
        conditions are met by the input.
        """
        if self.concent and self.parent and not self.parent.enabled_for(inpt):
            return False

        func = self.__enabled_func()
        return func(cond(inpt) for cond in self.conditions)

    def save(self):
        if self.manager:
            self.manager.update(self)

    @property
    def changes(self):
        return dict(list(self.__changes()))

    @property
    def changed(self):
        return bool(list(self.__changes()))

    def reset(self):
        self.__init_vars = vars(self).copy()

    def init_vars_items(self):
        for key, value in self.__init_vars.items():
            if key is '_Switch__init_vars':
                continue
            else:
                yield ()

    def __enabled_func(self):
        if self.compounded:
            return all
        else:
            return any

    def __changes(self):
        for key, value in self.__init_vars.items():
            if key is '_Switch__init_vars':
                continue
            elif key not in vars(self) or getattr(self, key) != value:
                yield (key, dict(previous=value, current=getattr(self, key)))


class Condition(object):
    """
    A Condition is the configuration of an argument and an operator, and tells
    you if the operator applies to the argument as it exists in the input
    instance passed in.  The previous sentence probably doesn't make any sense,
    so read on!

    The argument defines what this condition is checking.  Perhaps it's the
    request's IP address or the user's name.  Literally, an argumenet is an
    unbound function attached to an available Input class.  For example, for the
    request IP address, you would define an ``ip`` function inside the
    ``RequestInput`` class, and that function object, ``RequestInput.ip`` would
    be the Condition's argument,.

    When the Condition is called, it extracts the same argument from the passed
    in Input.  The extacted ``value`` is then checked against the operator.  An
    operator will tell you if the value meets **its** criteria, like if the
    value is > some number or within a range or percetnage.

    To put it another way, say you wanted a condition to only allow your switch
    to people between 15 and 30 years old.  To make the condition:

        1. You would create a ``UserInput`` class wraps your own User object,
            with a ``age`` method which returns the user's age.
        2. You would then create a new Condition via:
           ``Condition(argument=UserInput.age, operator=Between(15, 30))``.
        3. You then call that condition with an **instance** of a ``UserInput``,
           and it would return True if the age of the user the ``UserInput``
           class wraps is between 15 and 30.
    """

    def __init__(self, argument, operator, negative=False):
        self.argument = argument
        self.operator = operator
        self.negative = negative

    def __call__(self, inpt):
        if not self.__is_same_class_as_argument(inpt):
            return False

        application = self.__apply(inpt)

        if self.negative:
            application = not application

        return application

    def __apply(self, inpt):
        value = self.argument(inpt)
        return self.operator.applies_to(value)

    def __is_same_class_as_argument(self, inpt):
        return inpt.__class__ is self.argument.im_class


class Manager(object):
    """
    The Manager holds all state for Gargoyle.  It knows what Switches have been
    registered, and also what Input objects are currently being applied.  It
    also offers an ``active`` method to ask it if a given switch name is
    active, given its conditions and current inputs.
    """

    key_separator = ':'

    def __init__(self, storage, autocreate=False, switch_class=Switch):
        self.__switches = storage
        self.autocreate = False
        self.inputs = []
        self.switch_class = switch_class

    @property
    def switches(self):
        return self.__switches.values()

    def switch(self, name):
            return self.__get_switch_by_name(name)

    def register(self, switch, signal=signals.switch_registered):
        self.__sync_parental_relationships(switch)
        switch.manager = self
        self.__switches[switch.name] = switch
        signal.call(switch)

    def unregister(self, name):
        for child in self.__switches[name].children:
            self.unregister(child.name)

        to_delete = self.__switches[name]
        del self.__switches[name]
        signals.switch_unregistered.call(to_delete)

    def input(self, *inputs):
        self.inputs = list(inputs)

    def flush(self):
        self.inputs = []

    def active(self, name):
        switch = self.__get_switch_by_name(name)
        return any(switch.enabled_for(inpt) for inpt in self.inputs)

    def update(self, switch):
        self.register(switch, signal=signals.switch_updated)

        if switch.changes.get('name'):
            old_name = switch.changes['name'].get('previous')
            del self.__switches[old_name]

        switch.reset()

    def __create_and_register_disabled_switch(self, name):
        switch = self.switch_class(name)
        switch.state = self.switch_class.states.DISABLED
        self.register(switch)
        return switch

    def __sync_parental_relationships(self, switch):
        new_parent = self.__switches.get(self.__parent_key_for(switch))
        old_parent = switch.parent

        switch.parent = new_parent

        if old_parent and old_parent is not new_parent:
            old_parent.children.remove(switch)

        if new_parent:
            new_parent.children.append(switch)

    def __parent_key_for(self, switch):
        # TODO: Make this a method on the switch object
        parent_parts = switch.name.split(self.key_separator)[:-1]
        return self.key_separator.join(parent_parts)

    def __get_switch_by_name(self, name):
        try:
            return self.__switches[name]
        except KeyError:
            if not self.autocreate:
                raise ValueError("No switch named '%s' registered" % name)

            return self.__create_and_register_disabled_switch(name)
