import unittest
from nose.tools import *
import mock

from gargoyle.client.settings import manager
import gargoyle.client.models


class TestGargoyle(unittest.TestCase):

    other_engine = dict()

    def setUp(self):
        self.manager_defaults = dict(storage=manager.storage_engine,
                                     autocreate=manager.autocreate,
                                     operators=manager.operators,
                                     inputs=manager.inputs)

    def tearDown(self):
        manager.storage = self.manager_defaults['storage']
        manager.autocreate = self.manager_defaults['autocreate']
        manager.operators = self.manager_defaults['operators']
        manager.inputs = self.manager_defaults['inputs']

    def test_gargoyle_global_is_a_switch_manager(self):
        reload(gargoyle.client.singleton)
        self.assertIsInstance(gargoyle.client.singleton.gargoyle,
                              gargoyle.client.models.Manager)

    def test_consructs_manager_with_defaults_from_settings(self):
        with mock.patch('gargoyle.client.models.Manager') as init:
            init.return_value = None
            reload(gargoyle.client.singleton)
            expected = ((), self.manager_defaults)
            eq_(init.call_args, expected)

    def test_can_change_settings_before_importing(self):
        with mock.patch('gargoyle.client.models.Manager') as init:
            init.return_value = None
            manager.storage_engine = self.other_engine
            manager.autocreate = True
            manager.inputs = [4]
            manager.operators = [5]
            reload(gargoyle.client.singleton)
            expected = ((), dict(storage=self.other_engine, autocreate=True, inputs=[4], operators=[5]))
            eq_(init.call_args, expected)
