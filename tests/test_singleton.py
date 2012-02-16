import unittest
from nose.tools import *
import mock

from gargoyle.settings import manager
import gargoyle.models


class TestGargoyle(unittest.TestCase):

    other_engine = dict()

    def setUp(self):
        self.manager_defaults = dict(storage=manager.storage_engine,
                                     autocreate=manager.autocreate)

    def tearDown(self):
        manager.storage = self.manager_defaults['storage']
        manager.autocreate = self.manager_defaults['autocreate']

    def test_gargoyle_global_is_a_switch_manager(self):
        reload(gargoyle.singleton)
        self.assertIsInstance(gargoyle.singleton.gargoyle,
                              gargoyle.models.Manager)

    def test_consructs_manager_with_storage_engine_and_autocreate_from_settings(self):
        with mock.patch('gargoyle.models.Manager') as init:
            init.return_value = None
            reload(gargoyle.singleton)
            expected = ((), self.manager_defaults)
            eq_(init.call_args, expected)

    def test_can_change_settings_before_importing(self):
        with mock.patch('gargoyle.models.Manager') as init:
            init.return_value = None
            manager.storage_engine = self.other_engine
            manager.autocreate = True
            reload(gargoyle.singleton)
            expected = ((), dict(storage=self.other_engine, autocreate=True))
            eq_(init.call_args, expected)
