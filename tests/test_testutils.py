import unittest2
from nose.tools import *

from gutter.client.singleton import gutter
from gutter.client.testutils import switches
from gutter.client.models import Switch

from exam.decorators import around
from exam.cases import Exam


class TestDecorator(Exam, unittest2.TestCase):

    @around
    def add_and_remove_switch(self):
        gutter.register(Switch('foo'))
        yield
        gutter.flush()

    @switches(foo=True)
    def with_decorator(self):
        return gutter.active('foo')

    def without_decorator(self):
        return gutter.active('foo')

    def test_decorator_overrides_switch_setting(self):
        eq_(self.without_decorator(), False)
        eq_(self.with_decorator(), True)

    def test_context_manager_overrides_swich_setting(self):
        eq_(gutter.active('foo'), False)

        with switches(foo=True):
            eq_(gutter.active('foo'), True)
