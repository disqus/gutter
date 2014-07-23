import unittest2

from exam.cases import Exam
from exam.decorators import fixture

from gutter.client.encoding import (
    SwitchProtobufEncoding
)
from gutter.client.models import (
    Switch,
)

class ProtobufEncodingTest(Exam, unittest2.TestCase):

    switch = fixture(Switch, 'test')
    encoding = fixture(SwitchProtobufEncoding)

    def cycle(self, thing):
        return self.encoding.decode(
            self.encoding.encode(thing)
        )

    def test_it_encodes_and_decodes_correctly(self):
        self.assertEqual(self.switch, self.cycle(self.switch))
