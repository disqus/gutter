import unittest
from nose.tools import *
from tests import fixture
from gargoyle.wsgi import EnabledSwitchesMiddleware, signals
from gargoyle.singleton import gargoyle as singleton_gargoyle
import mock
import threading

from werkzeug.test import Client


class BaseTest(unittest.TestCase):

    @fixture
    def switch_active_signal_args(self):
        return []

    def signaling_wsgi_app(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        for args in self.switch_active_signal_args:
            signals.switch_active.call(*args)

        yield 'Hello World\n'

    def tearDown(self):
        signals.switch_active.reset()

    @fixture
    def middleware_app(self):
        return EnabledSwitchesMiddleware(self.signaling_wsgi_app)

    @fixture
    def client(self):
        return Client(self.middleware_app)

    def start_response(self, status, headers):
        return mock.Mock()


class TestInterface(BaseTest):

    def test_it_is_constructed_with_an_application(self):
        ware = EnabledSwitchesMiddleware('app')
        ware.application = 'app'

    def test_can_be_constructed_with_a_gargoyle_instance(self):
        ware = EnabledSwitchesMiddleware('app', 'gargoyle')
        ware.gargoyle = 'gargoyle'

    def test_uses_gargoyle_singleton_if_constructed_with_no_gargoyle(self):
        ware = EnabledSwitchesMiddleware('app')
        eq_(ware.gargoyle, singleton_gargoyle)

    def test_is_callable_with_environ_and_start_response(self):
        self.middleware_app('environ', self.start_response)

    def test_calls_app_with_same_environ(self):
        self.middleware_app.application = mock.Mock()

        for chunk in self.middleware_app('environ', self.start_response):
            yield

        call_args = self.middleware_app.application.call_args
        eq_(call_args[0][0], 'environ')


class TestSwitchTracking(BaseTest):

    @fixture
    def switch_active_signal_args(self):
        return [
            ('switch', 'inpt'),
            ('switch2', 'inpt2')
        ]

    def call_and_get_headers(self):
        start_response = mock.Mock()
        self.middleware_app('environ', start_response)
        return dict(start_response.call_args[0][1])

    @fixture
    def gargoyle_header(self):
        return self.call_and_get_headers()['X-Gargoyle-Switch']

    def test_calls_start_response_with_x_gargoyle_switches_header(self):
        ok_('X-Gargoyle-Switch' in self.call_and_get_headers())

    def test_adds_comma_separated_list_of_switches_to_x_gargoyle_header(self):
        eq_(self.gargoyle_header, 'active=switch,switch2')

    def test_returns_empty_active_list_when_no_switches_are_applied(self):
        self.switch_active_signal_args = []
        eq_(self.gargoyle_header, 'active=')

    def test_does_not_stop_other_global_switch_active_signals(self):
        global_called = []

        def update_called(switch, inpt):
            global_called.append(switch)

        signals.switch_active.connect(update_called)

        self.call_and_get_headers()
        self.call_and_get_headers()

        ok_(len(global_called) is 4)

    def test_signals_do_not_leak_between_threads(self):
        switch_headers = []
        app = EnabledSwitchesMiddleware(self.signaling_wsgi_app)

        def run_app():
            body, status, headers = Client(app).get('/')
            switch_headers.append(dict(headers)['X-Gargoyle-Switch'])

        threads = [threading.Thread(target=run_app) for i in range(2)]

        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        eq_(switch_headers, ['active=switch,switch2', 'active=switch,switch2'])