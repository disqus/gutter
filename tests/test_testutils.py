import unittest2
from durabledict import MemoryDict
from nose.tools import *

from gutter.client import get_gutter_client
from gutter.client.encoding import JsonPickleEncoding
from gutter.client.testutils import switches
from gutter.client.models import Switch

from exam.decorators import around, fixture
from exam.cases import Exam


class TestDecorator(Exam, unittest2.TestCase):

    @fixture
    def gutter(self):
        return get_gutter_client(
            alias=None,
            storage=MemoryDict(encoding=JsonPickleEncoding)
        )

    @around
    def add_and_remove_switch(self):
        self.gutter.register(Switch('foo'))
        yield
        self.gutter.flush()


    def without_decorator(self):
        return self.gutter.active('foo')

    def test_decorator_overrides_switch_setting(self):

        with_decorator = switches(foo=True, gutter=self.gutter)(self.without_decorator)

        eq_(self.without_decorator(), False)
        eq_(with_decorator(), True)

    def test_context_manager_overrides_swich_setting(self):
        eq_(self.gutter.active('foo'), False)

        with switches(foo=True, gutter=self.gutter):
            eq_(self.gutter.active('foo'), True)
