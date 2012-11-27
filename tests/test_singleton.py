import unittest
from nose.tools import *
import mock

from gargoyle.client.settings import manager
import gargoyle.client.models

from exam.decorators import after, around
from exam.cases import Exam


class TestGargoyle(Exam, unittest.TestCase):

    other_engine = dict()
    manager_defaults = dict(
        storage=manager.storage_engine,
        autocreate=manager.autocreate,
        operators=manager.operators,
        inputs=manager.inputs
    )

    @after
    def reset_to_defaults(self):
        for key, val in self.manager_defaults.items():
            setattr(manager, key, val)

    @around
    def preserve_default_singleton(self):
        import gargoyle.client.singleton
        original_singleton = gargoyle.client.singleton.gargoyle
        yield
        gargoyle.client.singleton.gargoyle = original_singleton

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
            expected = (
                (),
                dict(
                    storage=self.other_engine,
                    autocreate=True,
                    inputs=[4],
                    operators=[5]
                )
            )
            eq_(init.call_args, expected)

    def test_uses_default_manager_if_set(self):
        manager.default = mock.sentinel.default_manager
        reload(gargoyle.client.singleton)
        eq_(gargoyle.client.singleton.gargoyle, mock.sentinel.default_manager)