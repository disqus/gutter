import unittest
import os

from django.template import Context, Template  # TemplateSyntaxError

from exam.decorators import fixture, before, around
from exam.cases import Exam

from gargoyle.client.models import Switch
import gargoyle.client.singleton

os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
INSTALLED_APPS = ('gargoyle.client',)


class TempateTagTest(Exam, unittest.TestCase):

    @around
    def maintain_manager_state(self):
        self.gargoyle.register(self.switch)
        yield
        self.gargoyle.flush()

    @before
    def reload_singleton(self):
        reload(gargoyle.client.singleton)

    @fixture
    def gargoyle(self):
        return gargoyle.client.singleton.gargoyle

    @fixture
    def switch(self):
        return Switch('test', state=Switch.states.GLOBAL)

    @fixture
    def vanilla_ifswitch(self):
        return Template(
            """
            {% load gargoyle %}
            {% ifswitch test %}
            hello world!
            {% endifswitch %}
            """
        )

    def render(self, template):
        return template.render(Context())

    def assertContentInTemplate(self, content):
        rendered = self.render(self.vanilla_ifswitch)
        self.assertIn(content, rendered)

    def test_does_not_render_content_with_disabled_switch(self):
        self.assertContentInTemplate('hello world')

    def test_defaults_to_false_for_incorrect_switc_names(self):
        pass

