import unittest
from nose.tools import *
import mock

from chimera.client.settings import manager
import chimera.client.models

from exam.decorators import after, around
from exam.cases import Exam


class TestChimera(Exam, unittest.TestCase):

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
        import chimera.client.singleton
        original_singleton = chimera.client.singleton.chimera
        yield
        chimera.client.singleton.chimera = original_singleton

    def test_chimera_global_is_a_switch_manager(self):
        reload(chimera.client.singleton)
        self.assertIsInstance(chimera.client.singleton.chimera,
                              chimera.client.models.Manager)

    def test_consructs_manager_with_defaults_from_settings(self):
        with mock.patch('chimera.client.models.Manager') as init:
            init.return_value = None
            reload(chimera.client.singleton)
            expected = ((), self.manager_defaults)
            eq_(init.call_args, expected)

    def test_can_change_settings_before_importing(self):
        with mock.patch('chimera.client.models.Manager') as init:
            init.return_value = None
            manager.storage_engine = self.other_engine
            manager.autocreate = True
            manager.inputs = [4]
            manager.operators = [5]
            reload(chimera.client.singleton)
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
        reload(chimera.client.singleton)
        eq_(chimera.client.singleton.chimera, mock.sentinel.default_manager)