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

    # PY3
    __lt__ = __proxy_to_value_method('__lt__')
    __le__ = __proxy_to_value_method('__le__')
    __gt__ = __proxy_to_value_method('__gt__')
    __ge__ = __proxy_to_value_method('__ge__')
    __eq__ = __proxy_to_value_method('__eq__')
    __ne__ = __proxy_to_value_method('__ne__')
    __bool__ = __proxy_to_value_method('__bool__')

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

    def __lt__(self, other):
        return self.value < other

    def __gt__(self, other):
        return self.value > other

    def __eq__(self, other):
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __nonzero__(self, *args, **kwargs):
        return bool(self.value)

    __bool__ = __nonzero__

    @staticmethod
    def to_python(value):
        return str(value)
