import unittest
from nose.tools import *
from gargoyle import signals
from tests import fixture
import mock


class ActsLikeSignal(object):

    @fixture
    def callback(self):
        return mock.Mock(name="callback")

    @fixture
    def signal_with_callback(self):
        self.signal.connect(self.callback)
        return self.signal

    def test_signal_has_connect_callable(self):
        ok_(callable(self.signal.connect))

    def test_connect_raises_exceptiion_if_argument_is_not_callable(self):
        assert_raises(ValueError, self.signal.connect, True)

    def tests_callback_called_when_signal_is_called(self):
        self.signal_with_callback.call()
        self.callback.assert_called_once()

    def test_signal_passes_args_along_to_callback(self):
        self.signal_with_callback.call(1, 2.0, kw='args')
        self.callback.assert_called_once_with(1, 2.0, kw='args')


class TestSwitchRegisteredCallback(ActsLikeSignal, unittest.TestCase):

    @fixture
    def signal(self):
        return signals.switch_registered


class TestSwitchUnregisteredCallback(ActsLikeSignal, unittest.TestCase):

    @fixture
    def signal(self):
        return signals.switch_unregistered


class TestSwitchUpdatedCallback(ActsLikeSignal, unittest.TestCase):

    @fixture
    def signal(self):
        return signals.switch_updated


class TestConditionApplyErrorCallback(ActsLikeSignal, unittest.TestCase):

    @fixture
    def signal(self):
        return signals.switch_updated


class TestSwitchChecked(ActsLikeSignal, unittest.TestCase):

    @fixture
    def signal(self):
        return signals.switch_checked


class TestSwitchActive(ActsLikeSignal, unittest.TestCase):

    @fixture
    def signal(self):
        return signals.switch_active
