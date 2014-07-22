from gutter.client.operators import Base
from gutter.client.arguments.base import Container


class Registry(object):

    def __init__(self, cls):
        self.__items = {}
        self.__cls = cls

    items = property(lambda self: self.__items)

    def __getitem__(self, key):
        try:
            return self.__items[key]
        except KeyError:
            raise KeyError("Key '%s' not registered" % key)

    def register(self, key, obj):
        try:
            if not issubclass(obj, self.__cls):
                raise ValueError("%s is not a %s" % (obj, self.__cls))
        except TypeError:
            raise ValueError("%s is not a %s" % (obj, self.__cls))

        self.__items[key] = obj


def extract_key_from_name(func):
    def helpful_register(key_or_operator=None, operator=None):
        if not operator:
            operator = key_or_operator
            key = operator.name
        else:
            key = key_or_operator

        return func(key, operator)

    return helpful_register


arguments = Registry(Container)
operators = Registry(Base)


operators.register = extract_key_from_name(operators.register)
