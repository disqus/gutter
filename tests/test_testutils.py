import unittest
from nose.tools import *

from chimera.client.singleton import chimera
from chimera.client.testutils import switches
from chimera.client.models import Switch

from exam.decorators import around
from exam.cases import Exam


class TestDecorator(Exam, unittest.TestCase):

    @around
    def add_and_remove_switch(self):
        chimera.register(Switch('foo'))
        yield
        chimera.flush()

    @switches(foo=True)
    def with_decorator(self):
        return chimera.active('foo')

    def without_decorator(self):
        return chimera.active('foo')

    def test_decorator_overrides_switch_setting(self):
        eq_(self.without_decorator(), False)
        eq_(self.with_decorator(), True)

    def test_context_manager_overrides_swich_setting(self):
        eq_(chimera.active('foo'), False)

        with switches(foo=True):
            eq_(chimera.active('foo'), True)
