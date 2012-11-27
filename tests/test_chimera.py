import unittest

from nose.tools import *


class ChimeraTest(unittest.TestCase):

    def test_root_chimera_is_just_singleton(self):
        from chimera.client import chimera as root_chimera
        from chimera.client.singleton import chimera as singleton_chimera
        eq_(root_chimera, singleton_chimera)

    def test_root_autodiscover_is_just_autodiscovery_discover(self):
        from chimera.client import autodiscover as root_autodiscover
        from chimera.client.autodiscovery import discover as auto_discover
        eq_(root_autodiscover, auto_discover)
