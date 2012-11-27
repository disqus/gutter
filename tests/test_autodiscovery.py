import unittest

from exam.cases import Exam
from exam.helpers import mock_import

from chimera.client.autodiscovery import discover

from nose.tools import *


class AutodiscoverTest(Exam, unittest.TestCase):

    def run(self, *args, **kwargs):
        # Have to do this mock_import gymnastics because the imports inside the
        # autodiscovery module are local imports
        with mock_import('django.conf.settings') as mock_settings:
            mock_settings.INSTALLED_APPS = ['foo.bar']

            with mock_import('django.utils.importlib.import_module') as im:
                self.import_module = im
                super(AutodiscoverTest, self).run(*args, **kwargs)

    def test_autodiscover_attempts_to_import_chimera_in_installed_apps(self):
        discover()
        self.import_module.assert_called_once_with('foo.bar.chimera')

    def test_fails_silently_if_import_does_not_exist(self):
        self.import_module.side_effect = ImportError
        discover()  # No exception raised means it worked
