import unittest2

from mock import patch

from exam.cases import Exam
from exam.decorators import patcher

from gutter.client.decorators import switch_active

from nose.tools import *

from django.http import Http404


def my_view(request):
    return 'view called'


def decorated(*args, **kwargs):
    return switch_active('request', *args, **kwargs)(my_view)


class DecoratorTest(Exam, unittest2.TestCase):

    gutter = patcher(
        'gutter.client.decorators.default_gutter',
        **{'active.return_value': False}
    )

    def test_raises_a_404_error_if_switch_is_inactive(self):
        self.assertFalse(self.gutter.active('junk'))
        self.assertRaises(Http404, decorated(), 'junk')

    @patch('gutter.client.decorators.HttpResponseRedirect')
    def test_redirects_to_url_if_inactive_and_redirect_to_passed(self, httprr):
        self.assertFalse(self.gutter.active('junk'))
        eq_(decorated(redirect_to='location')('junk'), httprr.return_value)
        httprr.assert_called_once_with('location')

    def test_calls_the_function_if_switch_is_active(self):
        self.gutter.active.return_value = True
        eq_(decorated()('junk'), 'view called')
