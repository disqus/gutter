import random


class Base(object):

    def __init__(self, value):
        self.value = value

    def __proxy_to_value_method(method):
        def func(self, *args, **kwargs):

            if hasattr(self, 'value'):
                return getattr(self.value, method)(*args, **kwargs)
            else:
                raise NotImplementedError

        return func

    __cmp__ = __proxy_to_value_method('__cmp__')
    __hash__ = __proxy_to_value_method('__hash__')
    __nonzero__ = __proxy_to_value_method('__nonzero__')

    @staticmethod
    def to_python(value):
        return value


class Value(Base):
    pass


class Integer(Base):

    @staticmethod
    def to_python(value):
        return int(value)


class Float(Base):

    @staticmethod
    def to_python(value):
        return float(value)


class Boolean(Base):

    def __init__(self, value, hash_value=None):
        super(Boolean, self).__init__(value)
        self.hash_value = hash_value or random.getrandbits(128)

    def __hash__(self, *args, **kwargs):
        return hash(self.hash_value)

    @staticmethod
    def to_python(value):
        return bool(value)


class String(Base):

    def __cmp__(self, other):
        return cmp(self.value, other)

    def __nonzero__(self, *args, **kwargs):
        return bool(self.value)

    @staticmethod
    def to_python(value):
        return str(value)
