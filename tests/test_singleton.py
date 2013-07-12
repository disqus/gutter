import unittest2
from nose.tools import *
import mock

from gutter.client.settings import manager
import gutter.client.models

from exam.decorators import after, around
from exam.cases import Exam


class TestGutter(Exam, unittest2.TestCase):

    other_engine = dict()
    manager_defaults = dict(
        storage=manager.storage_engine,
        autocreate=manager.autocreate,
        inputs=manager.inputs
    )

    @after
    def reset_to_defaults(self):
        for key, val in self.manager_defaults.items():
            setattr(manager, key, val)

    @around
    def preserve_default_singleton(self):
        import gutter.client.singleton
        original_singleton = gutter.client.singleton.gutter
        yield
        gutter.client.singleton.gutter = original_singleton

    def test_gutter_global_is_a_switch_manager(self):
        reload(gutter.client.singleton)
        self.assertIsInstance(gutter.client.singleton.gutter,
                              gutter.client.models.Manager)

    def test_consructs_manager_with_defaults_from_settings(self):
        with mock.patch('gutter.client.models.Manager') as init:
            init.return_value = None
            reload(gutter.client.singleton)
            expected = ((), self.manager_defaults)
            eq_(init.call_args, expected)

    def test_can_change_settings_before_importing(self):
        with mock.patch('gutter.client.models.Manager') as init:
            init.return_value = None
            manager.storage_engine = self.other_engine
            manager.autocreate = True
            manager.inputs = [4]
            manager.operators = [5]
            reload(gutter.client.singleton)
            expected = (
                (),
                dict(
                    storage=self.other_engine,
                    autocreate=True,
                    inputs=[4],
                )
            )
            eq_(init.call_args, expected)

    def test_uses_default_manager_if_set(self):
        manager.default = mock.sentinel.default_manager
        reload(gutter.client.singleton)
        eq_(gutter.client.singleton.gutter, mock.sentinel.default_manager)