Gargoyle-Client
--------

**NOTE:** This repo is the client for the upcoming Gargoyle 2 release.  It does not work with the exsiting `Gargoyle 1 codebase <https://github.com/disqus/gargoyle/>`_.

Gargoyle-Client is feature swtich management library.  It allows users to create feature swtiches and setup conditions those switches will be enabled for.  Once configured, switches can then be checked against inputs (requests, user objects, etc) to see if the switches are active.

Table of Contents
=================

* Configuration_
* Setup_
* Inputs_
* `Switches`_
* `Conditions`_
* `Checking Switches as Active`_
* Signals_
* Namespaces_
* Templates_
* `Testing Utilities`_

Configuration
=============

Gargoyle-client requires a small bit of configuration before usage.

Choosing Storage
~~~~~~~~~~~~~~~~

Switches are persisted in a ``storage`` object, which is a `dict` or any object which provides the ``types.MappingType`` interface (``__setitem__`` and ``__getitem__`` methods).  By default, ``gargoyle-client`` uses an instance of `MemoryDict` from the `modeldict library <https://github.com/disqus/modeldict>`_.  This engine **does not persist data once the process ends** so a more persistant data store should be used.

Autocreate
~~~~~~~~~~

``gargoyle-client`` can also "autocreate" switches.  If ``autocreate`` is enabled, and ``gargoyle-client`` is asked if the switch is active but the switch has not been created yet, ``gargoyle-client`` will create the switch automatically.  When autocreated, a switch's state is set to "disabled."

This behavior is off by default, but can be enabled through a setting.  More on "settings" below.

Configuring Settings
~~~~~~~~~~~~~~~~~~~~

To change the ``storage`` and/or ``autocreate`` settings, simply import the settings module and set the appropriate variables:

.. code:: python

    from gargoyle.client.settings import manager as manager_settings
    from modeldict.dict import RedisDict
    from redis import RedisClient

    manager_settings.storage_engine = RedisDict('gargoyle', RedisClient()))
    manager_settings.autocreate = True

In this case, we are changing the engine to modeldict's ``RedisDict`` and turning on ``autocreate``.  These settings will then apply to all newly constructed ``Manager`` instances.  More on what a ``Manager`` is and how you use it later in this document.

Setup
=====

Once the ``Manager``'s storage engine has been condfigured, you can import gargoyle-client's singleton ``Manager`` object, which is your main interface with ``gargoyle-client``:

.. code:: python

    from gargoyle.client.singleton import gargoyle

At this point the ``gargoyle`` object is an instance of the ``Manager`` class, which holds all methods to register switches and check if they are active.  In most installations and usage scenarios, the ``gargoyle`` singleton will be your main interface.

Using a different default Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you would like to construct a use a different default manager, but still have it accessible via ``gargoyle.client.singleton.gargoyle``, you can construct and then assign a ``Manager`` instance to ``settings.manager.default`` value:

.. code:: python

    from gargoyle.client.settings import manager as manager_settings
    from gargoyle.client.models import Manager

    manager_settings.default = Manager({})   # Must be done before importing the singleton

    from gargoyle.client.singleton import gargoyle

    assert manager_settings.default == gargoyle

Note that the ``settings.manager.default`` value must be set **before** importing the singleton ``gargoyle`` instance.

Inputs
======

The first step in your usage of ``gargoyle-client`` should be to define your Inputs that you will be checking switches against.  An "Input" is an object which understands the business logic and object in your system (users, requests, etc) and knows how to validate and transform them into arguments for ``Switch`` conditions.

For instance, your system may have a ``User`` object that has properties like ``is_admin``, ``date_joined``, etc.  To switch against it, you would then create a ``UserInput`` object, which wraps a ``User`` instance, and provides an API of methods that return ``Argument`` objects:

.. code:: python

    from gargoyle.client.input import Base
    from gargoyle.client.input.arguments import String, Boolean, Value

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

1. An ``Input`` object has some number methods defined, which return the values you want to check a ``Switch`` conditions against.  In the above example, we'll want to make some switches active based on a user's ``name``, ``is_admin`` status and ``age``.
2. Methods **must** return an instance of an ``Argument`` object.  All arguments must subclass ``gargoyle.input.arguments.Base``.  At present there are 3 subclasses: ``Value`` for general values, ``Boolean`` for boolean values and ``String`` for string values.
3. ``Argument`` objects understand ``Switch`` conditions and operators, and implement the correct magic methods which allow themselves to be appropriatly compared.

By default, any callable public attribute of an ``Input`` is considered an argument. Subclasses that wish to change that behavior must implement their own implementation of the``arguments`` property on their ``Input`` subclass.

Rationale for Inputs
~~~~~~~~~~~~~~~~~~~~

You might be asking, why have these ``Input`` objects at all?  They seem to just wrap an object in my system and provide the same API.  Why can't I just use my business object **itself** and compare it against my switch conditions?

The short answer is that ``Input`` objects provide a translation layer to translate your business objects into objects that ``gargoyle-client`` understand.  This is important for a couple reasons.

First, it means you don't clutter your business logic or objects with code to support ``gargoyle-client``.  You declare all the arguments you wish to provide to switches in one location whose single responsibilty it to interface with ``gargoyle-client``.

Secondly, and most importantly, returning ``Argument`` objects ensures that ``gargoyle-client`` conditions work correctly.  This is mostly relevant to the percentage-based operators, and is best illustrated with an
example.

Imagine you have a ``User`` class with an ``is_vip`` boolean field.  Let's say you wanted to turn on a feature for only 10% of your VIP customers.  To do that, you would write a condition that says, "10% of the time when I'm called with the argument, I should be true."  That line of code would probably do something like this:

.. code:: python

    return 0 <= (hash(argument) % 100) < 10

The issue is that if ``argument == True``, then ``hash(argument) % 100`` will always be the same value for **every** ``User`` with ``is_vip`` of ``True``:

.. code:: python

    >>> hash(True)
    1
    >>> hash(True) % 100
    1

This is because in Python `True` objects alaways have the same hash value, and thus the percentage check doesn't work.  This is not the behavior you want.

For the 10% percentage range, you want it to be active for 10% of the inputs.  Therefore, each input must have a unique hash value, exactly the feature the ``Boolean`` argument provides.  Every ``Argument`` has known characteristics against conditions, while your objects may not.

That said, you don't absolutely **have** to use ``Argument`` objects.  For obvious cases, like ``use.age > some_value`` your ``User`` instance will work just fine, but to play it safe you should use ``Argument`` objects.  Using ``Argument`` objects also ensure that if you updatate ``gargoyle-client`` any new ``Operator`` types that are added will work correctly with your ``Argument``s.

Switches
============================================

Switches encapsulate the concept of an item that is either 'on' or 'off' depending on the input.  The swich determines its on/off status by checking each of its ``conditions`` and seeing if it applies to a certain input.

Switches are constructed with only one required argument, a ``name``:

.. code:: python

    from gargoyle.client.models import Switch

    switch = Switch('my cool feature')

Switches can be in 3 core states: ``GLOBAL``, ``DISABLED`` and ``SELECTIVE``.  In the ``GLOBAL`` state, the Switch is enabled for every input no matter what.  ``DISABLED`` Switches are not **disabled** for any input, no matter what.  ``SELECTIVE`` Switches enabled based on their conditions.

Swiches can be constructed in a certain state or the property can be changed later:

.. code:: python

    switch = Switch('new feature', state=Switch.states.DISABLED)
    another_switch = Switch('new feature')
    another_switch.state = Switch.states.DISABLED

Compounded
~~~~~~~~~~

When in the ``SELECTIVE`` state, normally only one condition needs be true for the Switch to be enabled for a particular input. If ``switch.componded`` is set to ``True``, then **all** of the switches conditions need to be true in order to be enabled::

    switch = Switch('require alll conditions', compounded=True)

Heriarchical Switches
~~~~~~~~~~~~~~~~~~~~~

You can create switches using a specific heirarchical naming scheme.  Switch namespaces are divided by the colon character (":"), and heirarchies of switches can be constructed in this fashion:

.. code:: python

    parent = Switch('movies')
    child1 = Switch('movies:star_wars')
    child2 = Switch('movies:die_hard')
    grandchild = Switch('movies:star_wars:a_new_hope')

In the above example, the ``child1`` switch is a child of the ``"movies"`` switch because it has ``movies:`` as a prefix to the switch name.  Both ``child1`` and ``child2`` are "children of the parent ``parent`` switch.  And ``grandchild`` is a child of the ``child1`` switch, but *not* the ``child2`` switch.

Concent
~~~~~~~

By default, each switch makes its "am I active?" decision independent of other switches in the Manager (including its parent), and only consults its own conditions to check if it is enabled for the Input.  However, this is not always the case.  Perhaps you have a cool new feature that is only available to a certain class of user.  And of *those* users, you want 10% to be be exposed to a different user interface to see how they behave vs the other 90%.

``gargoyle-client`` allows you to set a ``concent`` flag on a switch that instructs it to check its parental switch first, before checking itself.  If it checks its parent and it is not enabled for the same input, the switch immediatly returns ``False``.  If its parent *is* enabled for the input, then the switch will continue and check its own conditions, returning as it would normally.

For example:

.. code:: python

    parent = Switch('cool_new_feature')
    child = Switch('cool_new_feature:new_ui', concent=True)

For example, because ``child`` was constructed with ``concent=True``, even if ``child`` is enabled for an input, it will only return ``True`` if ``parent`` is **also** enbaled for that same input.

**Note:** Even switches in a ``GLOBAL`` or ``DISABLED`` state (see "Switch" section above) still concent their parent before checking themselves.  That means that even if a particular switch is ``GLOBAL``, if it has ``concent`` set to ``True`` and its parent is **not** enabled for the input, the switch itself will return ``False``.

Registering a Switch
~~~~~~~~~~~~~~~~~~~~

Once your ``Switch`` is constsructed with the right conditions, you need to retister it with a ``Manager`` instance to preserve it for future use.  Otherwise it will only exist in memory for the current process.  Register a switch via the ``register`` method on a ``Manager`` instance:

.. code:: python

    gargoyle.register(switch)

The Switch is now stored in the Manager's storage and can be checked if active through ``gargoyle.active(switch)``.

Updating a Switch
~~~~~~~~~~~~~~~~~

If you need to update your Switch, simply make the changes to the ``Switch`` object, then call the ``Manager``'s ``update()`` method with the switch to tell it to update the switch with the new object:

.. code:: python

    switch = Switch('cool switch')
    manager.register(switch)

    switch.name = 'even cooler switch'  # Switch has not been updated in manager yet

    manager.update(switch)  # Switch is now updated in the manager

Since this is a common pattern (retrieve switch from the manager, then update it), gargoyle-client provides a shorthand API in which you ask the manager for a switch by name, and then call ``save()`` on the **switch** to update it in the ``Manager`` it was retreived from:

.. code:: python

    switch = manager.switch('existing switch')
    switch.name = 'a new name'  # Switch is not updated in manager yet
    switch.save()  # Same as calling manager.update(switch)

Unregistering a Switch
~~~~~~~~~~~~~~~~~~~~~~

Existing switches may be removed from the Manager by calling ``unregister()`` with the switch name or switch instance:

.. code:: python

    gargoyle.unregister('deprecated switch')
    gargoyle.unregister(a_switch_instance)

**Note:** If the switch is part of a heirarchy and has children switches (see the "Heriarchical Switches" section abobve), all decendent switches (children, grandchildren, etc) will also be unregistered and deleted.


Conditions
==========

Each Swtich can have one-to-many conditions, which decribe the conditions under which that swtich is active.  ``Condition`` objects are constructed with two values: a ``argument`` and ``operator``

An ``argument`` is an ``Argument`` object returned from an ``Input`` class, like the one you defined earlier.  From the previous example, ``UserInput.age`` is an argument.  A condition's ``operator`` is some sort of check applied against that argument.  For instance, is the ``Argument`` greater than some value?  Equal to some value?  Within a range of values?  Etc.

Let's say you wanted a ``Condition`` that checks if the user's age is > 65 years old?  You would construct a Condition that way:

.. code:: python

    from gargoyle.client.operators.comparable import MoreThan

    condition = (Conditionargument=UserInput.age, operator=MoreThan(65))

This Condition will be true if any input instance has an ``age`` that is more than ``65``.

Please see the ``gargoyle.operators`` for a list of available operators.

Conditions can also be constructed with a ``negative`` argument, which negates the condition.  For example:

.. code:: python

    from gargoyle.client.operators.comparable import MoreThan

    condition = Condition(argument=UserInput.age, operator=MoreThan(65), negative=True)

This Condition is now ``True`` if the condition evaluates to ``False``.  In this case if the user's ``age`` is **not** more than ``65``.

Conditions then need to be appended to a swtich instance like so:

.. code:: python

    switch.conditions.append(condition)

You can append as many conditions as you would like to a swtich, there is no limit.

Checking Switches as Active
===========================

As stated before, switches are checked against **instances** of ``Input`` objects.  To do this, you would call the switch's ``enabled_for()`` method with the instance of your input.  You may call ``enabled_for()`` with any input instance, even ones where the Switch has no ``Condition`` for that class of ``Input``.  If the ``Switch`` is active for your input, ``enabled_for`` will return ``True``.  Otherwise, it will return ``False``.

``gargoyle.active()`` API
~~~~~~~~~~~~~~~~~~~~~~~~~

A common use case of gargoyle-client is to use it during the processing of a web request.  During execution of code, different code paths are taken depending on if certain swtiches are active or not.  Often times there are mutliple switches in existence at any one time and they all need to be checked against multiple arguments.  To handle this use case, Gargoyle provides a higher-level API.

To check if a ``Switch`` is active, simply call ``gargoyle.active()`` with the Switch name:

.. code:: python

    gargoyle.active('my cool feature')
    >>> True

The switch is checked against some number of ``Input`` objects.  Inputs can be added to the ``active()`` check one of two ways: locally, passed in to the ``active()`` call or globally, configured ahead of time.

To check agianst local inputs, ``active()`` takes any number of Input objects after the switch name to check the switch against.  In this example, the switch named ``'my cool feature'`` is checked against input objects ``input1`` and ``input2``:

.. code:: python

    gargoyle.active('my cool feature', input1, input2)
    >>> True

If you have global Input objects you would like to use for every check, you can set them up by calling the Manager's ``input()`` method:

.. code:: python

    gargoyle.input(input1, input2)

Now, ``input1`` and ``input2`` are checked against for every ``active`` call.  For example, assuming ``input1`` and ``input2`` are configured as above, this ``active()`` call would check if the Switch was enabled for inputs ``input1``, ``input2`` and ``input3`` in that order::

    gargoyle.active('my cool feature', input3)

Once you're doing using global inputs, perhaps at the end of a request, you should call the Manager's ``flush()`` method to remove all the inputs:

.. code:: python

    gargoyle.flush()

The Manager is now setup and ready for its next set of inputs.

When calling ``active()`` with a local ``Input``s, you can skip checking the ``Switch`` against the global inputs and **only** check against your locally passed in Inputs by passing ``exclusive=True`` as a keyword argument to ``active()``:

.. code:: python

    gargoyle.input(input1, input2)
    gargoyle.active('my cool feature', input3, exclusive=True)

In the above example, since ``exclusive=True`` is passed, the switch named ``'my cool feature'`` is **only** checked against ``input3``, and not ``input1`` or ``input2``.  The ``exclusive=True`` argument is not persistant, so the next call to ``active()`` without ``exclusive=True`` will again use the globally defined inputs.

Signals
=======

Gargoyle-client provides 4 total signals to connect to: 3 about changes to Switches, and 1 about errors applying Conditions.  They are all avilable from the ``gargoyle.signals`` module

Switch Signals
~~~~~~~~~~~~~~
There are 3 signals related to Switch changes:

1. ``switch_registered`` - Called when a new switch is registered with the Manager.
2. ``switch_unregistered`` - Called when a switch is unregistered with the Manager.
3. ``switch_updated`` - Called with a switch was updated.

To use a signal, simply call the signal's ``connect()`` method and pass in a callable object.  When the signal is fired, it will call your callable with the switch that is being register/unregistered/updated.  I.e.:

.. code:: python

    from gargoyle.client.signals import switch_updated

    def log_switch_update(switch):
        Syslog.log("Switch %s updated" % switch.name)

    switch_updated.connect(log_switch_updated)

Understanding Switch Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``switch_updated`` signal can be connected to in order to be notified when a switch has been changed.  To know *what* changed in the switch, you can consult its ``changes`` property:

.. code:: python

    >>> from gargoyle.client.models import Switch
    >>> switch = Switch('test')
    >>> switch.concent
    True
    >>> switch.concent = False
    >>> switch.name = 'new name'
    >>> switch.changes
    {'concent': {'current': False, 'previous': True}, 'name': {'current': 'new name', 'previous': 'test'}}

As you can see, when we changed the Switch's ``concent`` setting and ``name``, ``switch.changes`` reflects that in a dictionary of changed properties.  You can also simply ask the switch if anything has changed with the ``changed`` property.  It returns ``True`` or ``False`` if the switch has any changes as all.

You can use these values inside your signal callback to make decisions based on what changed.  I.e., email out a diff only if the changes include changed conditions.

Condition Application Error Signal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a ``Switch`` checks an ``Input`` object against its conditions, there is a good possibility that the ``Argument`` value may be some sort of unexpected value, and can cause an exception.  Whenever there is an exception raised during ``Condition`` checking itself against an ``Input``, the ``Condition`` will catch that exception and return ``False``.

While catching all exceptions is generally bad form and hides error, most of the time you do not want to fail an application request just because there was an error checking a switch condition, *especially* if there was an error during checking a ``Condition`` for which a user would not have applied in the first place.

That said, you would still probably want to know if there was an error checking a Condition.  To acomplish this, ``gargoyle``-client provides a ``condition_apply_error`` signal which is called when there was an error checking a ``Condition``.  The signal is called with an instance of the condition, the ``Input`` which caused the error and the instance of the Exception class itself:

.. code:: python

    signals.condition_apply_error.call(condition, inpt, error)

In your connected callback, you can do whatever you would like: log the error, report the exeception, etc.

Namespaces
==========

``gargoyle-client`` allows the use of "namespaces" to group switches under a single umbrealla, while both not letting one namespace see the switches of another namespace, but allowing them to share the same storage instance, operators and other configuration.

Given an existing vanilla ``Manager`` instance, you can create a namespaced manager by calling the ``namespaced()`` method:

.. code:: python

    notifications = gargoyle.namespaced('notifications')

At this point, ``notifications`` is a copy of ``gargoyle``, inheriting all of its:

* storage
* ``autocreate`` settting
* Global inputs
* Operators

It does **not**, however, share the same switches.  Newly constructed ``Manager`` instances are in the ``default`` namespace.  When ``namespaced()`` is called, ``gargoyle-client`` changes the manager's namespace to ``notifications``.  Any switches in the previous ``default`` namespace are not visible in the ``notifications`` namespace, and vice versa.

This allows you to have separate namespaced "views" of switches, possibly named the exact same name, and not have them comflict with each other.

Templates
=========

``gargoyle-client`` has a ``ifswitch`` template tag that you can use in your Django templates.  To use it, simply load the ``gargoyle`` template helpers and pass ``ifswitch`` the switch name.  If the switch is active, the content between ``ifswitch`` and ``endifswitch`` will be rendered.

.. code::

    {% load gargoyle %}
    {% ifswitch cool_feature %}
    switch active!
    {% endifswitch %}

You can also use an ``else`` tag to render content if the switch is not active:

.. code::

    {% load gargoyle %}
    {% ifswitch cool_feature %}
    switch active!
    {% else %}
    switch not active!
    {% endifswitch %}

Like ``gargoyle.active``, ``ifswitch`` takes any number of input objects to check the switch against:

.. code::

    {% load gargoyle %}
    {% ifswitch cool_feature user project %}
    switch active for user or project!
    {% endifswitch %}

NOTE: By default, the `gargoyle` instance used in the template tags is the ``gargoyle.client.singleton.gargoyle`` instance.

Testing Utilities
===============

If you would like to test code that uses ``gargoyle-client`` and have the ``gargoyle`` manager return predictable results, you can use the ``switches`` object from the ``testutils`` module.

The ``swtiches`` object can be used as both a context manager and a decorator.  It is passed ``kwargs`` of switch names and their``active`` return values.

For instance, with this code here, by passing ``cool_feature=True`` to the ``switches`` object as a context manager, any call to ``gargoyle.active('cool_feature')`` will return ``True``.  Calls to ``active()`` with other switch names will return their actual live switch status:

.. code:: python

    from gargoyle.client.testutils import switches
    from gargoyle.singleton import gargoyle

    with switches(cool_feature=True):
        gargoyle.active('cool_feature')  # True


And when using ``switches`` as a decorator:

.. code:: python

    from gargoyle.client.testutils import switches
    from gargoyle.singleton import gargoyle

    @switches(cool_feature=True)
    def run(self):
        gargoyle.active('cool_feature')  # True

Additionally, you may pass an alternamte ``Manager`` instance to ``switches`` to use that manager instead of the default one:

.. code:: python

    from gargoyle.client.testutils import switches
    from gargoyle.client.models import Manager

    my_manager = Manager({})

    @switches(my_manager, cool_feature=True)
    def run(self):
        gargoyle.active('cool_feature')  # True
