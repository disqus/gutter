Gargoyle-Client
--------

Gargoyle-Client is feature swtich management library.  It allows users to create feature swtiches and setup conditions those switches will be enabled for.  Once configured, switches can then be checked against inputs (requestss, user objects, etc) to see if the switches are active.

Configuration
=============

The only configuration that must be done for Gargoyle is to tell it what storage engine to use for storing its switches.  A storage can be any object that follows the dict protocol, i.e. an instance of `dict` or objects that provide ``__setitem__`` and ``__getitem__`` methods.  By default, gargoyle-client uses an instance of `MemoryDict` from the modeldict library.  This engine **does not persist data once the process ends** so a more persistant data store should be used.

To set the data store, simply import the settings module and set the appropriate variable.  In this case, we are changing the engine to modeldict's Redis dictionary type::

    from gargoyle.settings import manager
    from modeldict.dict import RedisDict
    from redis import RedisClient

    manager.storage_engine = RedisDict('gargoyle', RedisClient()))

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

1. An Input object has some number methods defined which return Arguments.  These methods define the values you want to check Switch conditions against.  In the above example, we'll want to make some switches active based on the user's name, admin status and age.
2. Methods must return an instance of an argument, a subclass of ``gargoyle.input.arguments.Base``.  At present there are 3 subclasses: ``Field`` for general values, ``Boolean`` for boolean values and ``String`` for string values.
3. Arguments understand Switch conditions and their operators, and implement the correct magic methods to allow themselves to be appropriatly compared.

By default, any callable public attribute of an Input considered an argument. Subclasses that which to change that behavior can implement their own implementation of the``arguments`` property.

Swithes and Conditions
============================================

The next phase of gargoyle-client usage is defining switches and conditions:

Switch
~~~~~~

Switches encapsulate the concept of an item that is either 'on' or 'off' depending on the input.  The swich it's on/off status by checking each of its conditions and seeing if it applies to a certain input.  Normally only one Condition needs be true for the Switch to be enabled for a particular input, but of ``switch.componded`` is set to True, then **all** of the switches conditions need to be true in order to be enabled.

Switches are constructed with only one argument, a ``name``::

    from gargoyle.models import Switch

    switch = Switch('my cool feature')

Condition
~~~~~~~~~

Each Swtich has 1 to many conditions, which decribe the conditions under which that swtich is active.  Condition objects are constructed with two values: a ``argument`` and ``operator``

An ``argument`` is an Argument object returned from an Input class, like the one you define earlier.  From the previous example, ``UserInput.age`` is an argument.  A condition's ``operator`` is some sort of check applied against that argument.  For instance, is the Argument greater than some value?  Equal to some value?  Within a range of values?  Etc.

For an example, let's say you wanted a Condition that check if the user's age is > 65 years old?  You would construct a Condition that way::

    from gargoyle.operators.comparable import MoreThan

    condition = Condition(argument=UserInput.age, operator=MoreThan(65))

This Condition will be true if any input instance has an ``age`` that is more than 65.

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