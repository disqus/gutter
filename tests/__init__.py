"""
gargoyle.tests
~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""


class fixture(object):
    """
    Works like the built in @property decorator, except that it caches the
    return value for each instance.  This allows you to lazy-load the fixture
    only if your test needs it, rather than having it setup before *every* test
    when put in the setUp() method or returning a fresh run of the decorated
    method, which 99% of the time isn't what you want.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            self.cache[args] = self.func(*args)
            return self.cache[args]

    def __get__(self, instance, klass):
        return self.__call__(instance)

from tests import *