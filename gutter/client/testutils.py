"""
gutter.testutils
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from functools import wraps
from gutter.client.singleton import gutter


class SwitchContextManager(object):
    """
    Allows temporarily enabling or disabling a switch.

    Ideal for testing.

    >>> @switches(my_switch_name=True)
    >>> def foo():
    >>>     print gutter.active('my_switch_name')

    >>> def foo():
    >>>     with switches(my_switch_name=True):
    >>>         print gutter.active('my_switch_name')

    You may also optionally pass an instance of ``SwitchManager``
    as the first argument.

    >>> def foo():
    >>>     with switches(gutter, my_switch_name=True):
    >>>         print gutter.active('my_switch_name')
    """
    def __init__(self, gutter=gutter, **keys):
        self.previous_active_func = gutter.active
        self.gutter = gutter
        self.keys = keys

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner

    def __enter__(self):

        def patched_active(gutter):
            real_active = gutter.active

            def wrapped(key, *args, **kwargs):
                if key in self.keys:
                    return self.keys[key]

                return real_active(key, *args, **kwargs)

            return wrapped

        self.gutter.active = patched_active(self.gutter)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.gutter.active = self.previous_active_func

switches = SwitchContextManager
