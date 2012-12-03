import unittest

from nose.tools import *


class GutterTest(unittest.TestCase):

    def test_root_gutter_is_just_singleton(self):
        from gutter.client.default import gutter as root_gutter
        from gutter.client.singleton import gutter as singleton_gutter
        eq_(root_gutter, singleton_gutter)

    def test_root_autodiscover_is_just_autodiscovery_discover(self):
        from gutter.client import autodiscover as root_autodiscover
        from gutter.client.autodiscovery import discover as auto_discover
        eq_(root_autodiscover, auto_discover)
