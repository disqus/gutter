"""
Python 3 compatibility.
"""

import six


if six.PY3:
    import unittest
    ifilter = filter
else:
    import unittest2 as unittest
    from itertools import ifilter


NoneType = type(None)


class TestCaseMixin(object):
    if six.PY3:
        def assertItemsEqual(self, actual, expected, msg=None):
            self.assertCountEqual(actual, expected, msg=None)
