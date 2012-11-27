from __future__ import absolute_import

from django import template
from gargoyle.client.singleton import gargoyle


register = template.Library()


def ifswitch(parser, token):
    try:
        bits = token.split_contents()
        (_,), (name,), inputs = bits[:1], bits[1:2], bits[2:]
    except ValueError:
        tag_name = token.contents.split()[0]
        format = "%r tag requires a switch name"
        raise template.TemplateSyntaxError(format % tag_name)

    if_true = parser.parse(('else', 'endifswitch'))
    if_false = template.NodeList()

    # If there is an "else" token, capture that as the "false" branch instead of
    # the empty node list
    if parser.next_token().contents == 'else':
        if_false = parser.parse(('endifswitch',))
        parser.delete_first_token()

    return SwitchNode(name, if_true, if_false, *inputs)


class SwitchNode(template.Node):

    def __init__(self, name, if_true, if_false, *inputs):
        self.name = name
        self.inputs = (template.Variable(i) for i in inputs)
        self.if_true = if_true
        self.if_false = if_false

    def render(self, context):
        if gargoyle.active(self.name, *self.resolved_inputs_for(context)):
            return self.if_true.render(context)
        else:
            return self.if_false.render(context)

    def resolved_inputs_for(self, context):
        return [i.resolve(context) for i in self.inputs]


register.tag('ifswitch', ifswitch)
