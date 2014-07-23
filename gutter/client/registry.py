from gutter.client.operators import Base
from gutter.client.arguments.base import Container


class SymmetricDict(object):
    """
    A dictionary-like data structure that maintains two mapping structures:

    * a mapping from keys to values, as well as
    * a mapping from values to keys.

    This adds a few constraints that are not found in a typical dictionary,
    since values will also be used as keys:

    * both keys and values must be an instance of a hashable type, and
    * values must be unique.

    This data structure also implements the full dictionary API, and can be
    a drop-in replacement for anywhere a dictionary would otherwise be used.

        >>> sd = SymmetricDict({
        ...     'a': 1,
        ...     'b': 2,
        ... })
        >>> sd['a']
        1
        >>> sd.get_key(1)
        'a'

    """
    def __init__(self, initial=()):
        self._keys = dict(initial)
        self._values = dict(reversed(item) for item in self._keys.iteritems())

    def __getitem__(self, key):
        return self._keys[key]

    def __setitem__(self, key, value):
        self._keys[key] = value
        self._values[value] = key

    def __delitem__(self, key):
        value = self._keys[key]
        del self._keys[key], self._values[value]

    def __getattr__(self, name):
        return getattr(self._keys, name)

    def __iter__(self):
        return iter(self._keys)

    def __contains__(self, item):
        return item in self._keys

    def get_key(self, value):
        """
        :raises: :exc:`KeyError` if the value does not exist
        :returns: key where ``value`` is stored
        """
        return self._values[value]


class Records(object):

    def __init__(self, check, cls):
        self.__check = check
        self.__items = SymmetricDict()
        self.__cls = cls

    items = property(lambda self: self.__items)

    def __getitem__(self, key):
        try:
            return self.__items[key]
        except KeyError:
            raise KeyError("Key '%s' not registered" % key)

    def get_key(self, obj):
        return self.__items.get_key(obj)

    def register(self, key, obj):
        try:
            if not self.__check(obj, self.__cls):
                raise ValueError("%s is not a %s" % (obj, self.__cls))
        except TypeError:
            raise ValueError("%s is not a %s" % (obj, self.__cls))

        self.__items[key] = obj


class Registry(object):

    def __init__(self):
        self.arguments = Records(issubclass, Container)
        self.operators = Records(isinstance, Base)
