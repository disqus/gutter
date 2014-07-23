from gutter.client.operators import Base
from gutter.client.arguments.base import Container


class Records(object):

    def __init__(self, check, cls):
        self.__check = check
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
            if not self.__check(obj, self.__cls):
                raise ValueError("%s is not a %s" % (obj, self.__cls))
        except TypeError:
            raise ValueError("%s is not a %s" % (obj, self.__cls))

        self.__items[key] = obj


class Registry(object):

    def __init__(self):
        self.arguments = Records(issubclass, Container)
        self.operators = Records(isinstance, Base)
