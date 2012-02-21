Gargoyle-Client
--------

**NOTE:** This repo is the client for the upcoming Gargoyle 2 release.  It does not work with the exsiting `Gargoyle 1 codebase <https://github.com/disqus/gargoyle/>`_.

Gargoyle-Client is feature swtich management library.  It allows users to create feature swtiches and setup conditions those switches will be enabled for.  Once configured, switches can then be checked against inputs (requestss, user objects, etc) to see if the switches are active.

Table of Contents
=================

* Configuration_
* Setup_
* Inputs_
* `Switches and Conditions`_
* `Checking Switches as Active`_
* Signals_

Configuration
=============

Gargoyle-client requires a small bit of configuration before usage.

Choosing Storage
~~~~~~~~~~~~~~~~

Switches are stored with a ``storage`` object, which is an instance of `dict` or any object which provides ``__setitem__`` and ``__getitem__`` methods.  By default, gargoyle-client uses an instance of `MemoryDict` from the modeldict library.  This engine **does not persist data once the process ends** so a more persistant data store should be used.

Autocreate
~~~~~~~~~~

Gargoyle-client can also autocreate switches if they are asked about their active state, but have not been officially created yet.  This behavior is off by default, but can be enabled through a setting.  When autocreated, a switch's state is set to "disabled."

Configuring Settings
~~~~~~~~~~~~~~~~~~~~

To change the ``storage`` and ``autocreate`` settings, simply import the settings module and set the appropriate variables::

    from gargoyle.settings import manager
    from modeldict.dict import RedisDict
    from redis import RedisClient

    manager.storage_engine = RedisDict('gargoyle', RedisClient()))
    manager.autocreate = True

In this case, we are changing the engine to modeldict's Redis dictionary type and turning on autocreate.

Setup
=====

Once the Manager's storage engine has been condfigured, you can import gargoyle-client's singleton Manager object, which is your main interface with gargoyle-client::

    from gargoyle.singleton import gargoyle

At this point the ``gargoyle`` object is an instance of the Manager class, which holds all methods to register switches and check if they are active.

Thread Safety
~~~~~~~~~~~~~

Please note that a globally shared Manager instance through the singleton is **not** thread safe.  If your usage of gargoyle-client requires multiple threads to use gargoyle-client, please instantiate a separate Manager instance per thread.

Inputs
======

The first step in your usage of gargoyle-client should be to define your Inputs that you will be checking switches against.  An Input is an object which understands the business objects in your system (users, requests, etc) and knows how to validate and transform them into arguments for Switch conditions.  For instance, you may have a User object that has properties like ``is_admin``, ``date_joined``, etc.  You would create an UserInput object, which wraps a User instance, and provides API methods, which return Argument objects::

    from gargoyle.input import Base
    from gargoyle.input.arguments import String, Boolean, Value

    class UserInput(Base):

        def __init__(self, user):
            self._user = user

        def name(self):
            return String(self._user.name)

        def is_admin(self):
            return Boolean(self._user.is_admin)

        def age(self):
            return Value(self._user.age)


There are a few things going on here, so let's break down what they all mean.

1. An Input object has some number methods defined, which return the values you want to check Switch conditions against.  In the above example, we'll want to make some switches active based on the user's name, admin status and age.
2. Methods must return an instance of an Argument object.  All arguments must subclass ``gargoyle.input.arguments.Base``.  At present there are 3 subclasses: ``Value`` for general values, ``Boolean`` for boolean values and ``String`` for string values.
3. Argument objects understand Switch conditions and operators, and implement the correct magic methods which allow themselves to be appropriatly compared.

By default, any callable public attribute of an Input considered an argument. Subclasses that which to change that behavior must implement their own implementation of the``arguments`` property.

Switches and Conditions
============================================

The next phase of gargoyle-client usage is defining switches and conditions:

Switch
~~~~~~

Switches encapsulate the concept of an item that is either 'on' or 'off' depending on the input.  The swich it's on/off status by checking each of its conditions and seeing if it applies to a certain input.

Switches are constructed with only one required argument, a ``name``::

    from gargoyle.models import Switch

    switch = Switch('my cool feature')

Switches can be in 3 core states: ``GLOBAL``, ``DISABLED`` and ``SELECTIVE``.  In the ``GLOBAL`` state, the Switch is enabled for every input no matter what.  ``DISABLED`` Switches are not enabled for any input, no matter what.  ``SELECTIVE`` Switches enabled based on their conditions.

Swiches can either be constructed in a certain state or the property can be changed later::

    switch = Switch('new feature', state=Switch.states.DISABLED)
    another_switch = Switch('new feature')
    another_switch.state = Switch.states.DISABLED

When in the ``SELECTIVE`` state, normally only one Condition needs be true for the Switch to be enabled for a particular input, but of ``switch.componded`` is set to True, then **all** of the switches conditions need to be true in order to be enabled::

    switch = Switch('require alll conditions', compounded=True)

Heriarchical Switches
~~~~~~~~~~~~~~~~~~~~~

You can create switches using a specific heirarchical naming scheme.  Switch namespaces are divided by the colon character (":"), and heirarchies of swithes can be constructed in this fashion::

    parent = Switch('movies')
    child1 = Switch('movies:star_wars')
    child2 = Switch('movies:die_hard')
    grandchild = Switch('movies:star_wars:a_new_hope')

In the above example, the ``"movies:star_wars"`` switch is a child of the ``"movies"`` switch because it has ``'movies:'`` as a prefix to the switch name.  Both ``"movies:start_wars"`` and ``"movies:die_hard"`` are "children of the parent ``"movies"`` switch.  And ``"'movies:star_wars:a_new_hope'"`` is a child of the ``"movies:star_wars"`` switch, but *not* the ``"'movies:die_hard'"`` switch.

By default, each switch is independent of other switches in the Manager (including its parent) and only consults its own conditions to check if it is enabled for the Input.  However, this is not always the case.  Perhaps you have a cool new feature that is only available to a certain class of user.  And of *those* users, you want 10% to be be exposed to a different user interface to see how they behave vs the other 90%.

gargoyle-client allows you to set a ``concent`` flag on a switch that instructs it to check its parental switch first, before checking itself.  If it checks its parent and it is not enabled for the same Input, the switch immediatly returns ``False``.  If its parent *is* enabled for the Input, then the switch will continue and check its own conditions, returning as it would normally.

For example::

    parent = Switch('cool_new_feature')
    child = Switch('cool_new_feature:new_ui', concent=True)

For example, because ``child`` was constructed with ``concent=True``, even if ``child`` is enabled for an Input, it will only return ``True`` if ``parent`` is also enbaled for that same input.

**Note:** Even switches in a ``GLOBAL`` or ``DISABLED`` state (see "Switch" section above) still concent their parent before checking themselves.  That means that even if a particular switch is ``GLOBAL``, if it is concenting and its parent is not enabled for the input, the switch itself will return that it is not enabled for the input.

Condition
~~~~~~~~~

Each Swtich has 1 to many conditions, which decribe the conditions under which that swtich is active.  Condition objects are constructed with two values: a ``argument`` and ``operator``

An ``argument`` is an Argument object returned from an Input class, like the one you define earlier.  From the previous example, ``UserInput.age`` is an argument.  A condition's ``operator`` is some sort of check applied against that argument.  For instance, is the Argument greater than some value?  Equal to some value?  Within a range of values?  Etc.

For an example, let's say you wanted a Condition that check if the user's age is > 65 years old?  You would construct a Condition that way::

    from gargoyle.operators.comparable import MoreThan

    condition = Condition(argument=UserInput.age, operator=MoreThan(65))

This Condition will be true if any input instance has an ``age`` that is more than 65.

Please see the ``gargoyle.operators`` for a list of available conditions.

Conditions can also be constructed with a ``negative`` argument, which negates the condition.  For example::

    from gargoyle.operators.comparable import MoreThan

    condition = Condition(argument=UserInput.age, operator=MoreThan(65), negative=True)

This Condition is now True if it evaluates to false.  In this case if the user's ``age`` is **not** more than 65.

Conditions then need to be appending to a swtich instance like so::

    switch.conditions.append(condition)

You can append as many conditions as you would like to a swtich

Registering a Switch
~~~~~~~~~~~~~~~~~~~~

Once your Switch is constsructed with the right conditions, you need to retister the Switch with your Manager instance to preserve it for future use.  Otherwise it will only exist in memory for the current process.  If you've imported your Manager instance it via the singleton, then it's likely the global ``gargoyle`` object::

    gargoyle.register(switch)

The Switch is now stored in the Manager's storage and can be checked if active.

Updating a Switch
~~~~~~~~~~~~~~~~~

If you need to update your Switch, simple make the changes to the Switch object, then call the Manager's ``update()`` method to tell it to update the switch with the new object::

    switch = Switch('cool switch')
    manager.register(switch)

    switch.name = 'even cooler switch'  # Switch has not been updated in manager yet

    manager.update(switch)  # Switch is now updated in the manager

Since this is a common pattern (retrieve switch from the manager, then update it), gargoyle-client provides a shorthand API in which you ask the Manager for a switch by name, and then call ``save()`` on the switch to update it in the Manager::

    switch = manager.switch('existing switch')
    switch.name = 'a new name'  # Switch is not updated in manager yet
    switch.save()  # Same as calling manager.update(switch)

Unregistering a Switch
~~~~~~~~~~~~~~~~~~~~~~

Existing switches may be removed from the Manager by calling ``unregister()`` with the switch name or switch instance::

    gargoyle.unregister('deprecated switch')
    gargoyle.unregister(a_switch_instance)

**Note:** If the switch is part of a heirarchy and has children switches (see the "Heriarchical Switches" section abobve), all decendent switches (children, grandchildren, etc) will also be unregistered and deleted.

Checking Switches as Active
===========================

As stated before, switches are checked against **instances** of Input objects.  To do this, you would call the switch's ``enabled_for()`` method with the instance of your input.  You may call ``enabled_for()`` with any input instance, even ones where the Switch has no Condition for that class of Input.  If the Switch is active for your input, ``enabled_for`` will return True.  Otherwise, it will return ``False``.

``gargoyle.active()`` API
~~~~~~~~~~~~~~~~~~~~~~~~~

A common use case of gargoyle-client is to use it during the processing of a web request.  During execution of code, different code paths are taken depending on if certain swtiches are active or not.  Iften times there are mutliple switches in existence at any one time and they all need to be checked against multiple arguments.  To handle this use case, Gargoyle provides a high level API.

To use the high level API, first add input instances to the Manager instance like so::

    gargoyle.input(input1, input2, inputn)

Then, to check if a Switch is active, simply call ``gargoyle.active()`` with the Switch name::

    gargoyle.active('my cool feature')
    >>> True

You may check as many switches as you like, and they all will be checked against the switches you registered with the ``input()`` call.

Once you're doing using these inputs, perhaps at the end of a request, you should call the Manager's ``flush()`` method to remove all the inputs::

    gargoyle.flush()

The Manager is now setup and ready for its next set of inputs.

Signals
=======

Gargoyle-client provides 4 total signals to connect to: 3 about changes to Switches, and 1 about errors applying Conditions.  They are all avilable from the ``gargoyle.signals`` module

Switch Signals
~~~~~~~~~~~~~~
There are 3 signals related to Switch changes:

1. ``switch_registered`` - Called when a new switch is registered with the Manager.
2. ``switch_unregistered`` - Called when a switch is unregistered with the Manager.
3. ``switch_updated`` - Called with a switch was updated.

To use a signal, simply call the signal's ``connect()`` method and pass in a callable object.  When the signal is fired, it will call your callable with the switch that is being register/unregistered/updated.  I.e.::

    from gargoyle.signals import switch_updated

    def log_switch_update(switch):
        Syslog.log("Switch %s updated" % switch.name)

    switch_updated.connect(log_switch_updated)

Understanding Switch Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``switch_updated`` signal can be connected to in order to be notified when a switch has been changed.  To know *what* changed in the switch, you can consult its ``changes`` property::

    >>> from gargoyle.models import Switch
    >>> switch = Switch('test')
    >>> switch.concent
    True
    >>> switch.concent = False
    >>> switch.name = 'new name'
    >>> switch.changes
    {'concent': {'current': False, 'previous': True}, 'name': {'current': 'new name', 'previous': 'test'}}

As you can see, when we changed the Switch's ``concent`` setting and ``name``, ``switch.changes`` reflects that in a dictionary of changed properties.  You can also simply ask the switch if anything has changed with the ``changed`` property.

You can use these values inside your signal callback to make decisions based on what changed.  I.e., email out a diff of the changed values.

Condition Application Error Signal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a Switch applies an Input object to its conditions, there is a good possibility that the Argument value may be some sort of unexpected value, and can cause an exception.  Whenever there is an exception raised during Condition checking itself against an Input, the Condition will catch that exception and return ``False``.

While catching all exceptions is generally bad form and hides error, most of the time you do not want to fail an application request just because there was an error checking a Switch Condition, *especially* if there was an error during checking a Condition for which a user would not have applied in the first place.

That said, you would still probably want to know if there was an error checking a Condition.  To acomplish this, gargoyle-client provides a ``condition_apply_error`` signal which is called when there was an error applying a Condition.  The signal is called with an instance of the condition, the Input which caused the error and the instance of the Exception class itself::

    signals.condition_apply_error.call(condition, inpt, error)

In your connected callback, you can do whatever you would like: log the error, report the exeception, etc.