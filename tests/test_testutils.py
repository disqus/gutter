import unittest
from nose.tools import *

from gargoyle.client.singleton import gargoyle
from gargoyle.client.testutils import switches
from gargoyle.client.models import Switch

from exam.decorators import around
from exam.cases import Exam


class TestDecorator(Exam, unittest.TestCase):

    @around
    def add_and_remove_switch(self):
        gargoyle.register(Switch('foo'))
        yield
        gargoyle.flush()

    @switches(foo=True)
    def with_decorator(self):
        return gargoyle.active('foo')

    def without_decorator(self):
        return gargoyle.active('foo')

    def test_decorator_overrides_switch_setting(self):
        eq_(self.without_decorator(), False)
        eq_(self.with_decorator(), True)

    def test_context_manager_overrides_swich_setting(self):
        eq_(gargoyle.active('foo'), False)

        with switches(foo=True):
            eq_(gargoyle.active('foo'), True)
