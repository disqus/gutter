import unittest2

from nose.tools import *


class GutterTest(unittest2.TestCase):

    def test_root_gutter_is_just_singleton(self):
        from gutter.client.default import gutter as root_gutter
        from gutter.client.singleton import gutter as singleton_gutter
        eq_(root_gutter, singleton_gutter)
