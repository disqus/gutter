import json

from gutter.client.models import (
    Condition,
    Switch,
)
from gutter.client.registry import Registry
from gutter.client.interfaces.interfaces_pb2 import (
    ConditionList as PBConditionList,
    Switch as PBSwitch,
)


class SwitchProtobufEncoding(object):

    def __init__(self):
        self.registry = Registry()

    def encode(self, switch):
        pbswitch = PBSwitch()

        pbswitch.name = switch.name

        if switch.label:
            pbswitch.label = switch.label

        pbswitch.concent = switch.concent
        pbswitch.state = switch.state

        if switch.compounded:
            pbswitch.conditions.quantifier = PBConditionList.ALL
        else:
            pbswitch.conditions.quantifier = PBConditionList.ANY

        for condition in switch.conditions:
            pbcondition = pbswitch.conditions.conditions.add()
            # XXX: TODO FIX ME v
            pbcondition.argument = self.registry.arguments.get_key(condition.argument)
            pbcondition.attribute = condition.attribute
            pbcondition.operator = self.registry.operators.get_key(condition.operator)
            pbcondition.negative = condition.negative

        return pbswitch.SerializeToString()

    def decode(self, data):
        pbswitch = PBSwitch()

        pbswitch.ParseFromString(data)

        switch = Switch(
            name=pbswitch.name,
            label=pbswitch.label,
            # XXX: This only works cause the numbers are synced. Should
            #      this change?
            state=pbswitch.state,
            concent=pbswitch.concent,
            compounded=pbswitch.conditions.quantifier == PBConditionList.ALL,
        )

        for pbcondition in pbswitch.conditions.conditions:
            condition = Condition(
                argument=self.registry.arguments[pbcondition.argument],
                attribute=pbcondition.attribute,
                operator=self.registry.operators[pbcondition.operator],
                negative=pbcondition.negative,
            )
            switch.conditions.append(condition)

        return switch


class SwitchJSONEncoding(object):

    def __init__(self):
        self.registry = Registry()

    def encode(self, switch):
        basicswitch = {
            'name': switch.name,
            'concent': switch.concent,
            'state': switch.state,
            'conditions': {'conditions': []}
        }

        if switch.label:
            basicswitch['label'] = switch.label

        if switch.compounded:
            basicswitch['conditions']['quantifier'] = 'all'
        else:
            basicswitch['conditions']['quantifier'] = 'any'

        for condition in switch.conditions:
            basiccondition = {
                'argument': self.registry.arguments.get_key(condition.argument),
                'attribute': condition.attribute,
                'operator': self.registry.operators.get_key(condition.operator),
                'negative': condition.negative
            }
            basicswitch['conditions']['conditions'].append(basiccondition)

        return json.dumps(basicswitch)

    def decode(self, json_string):
        data = json.loads(json_string)

        switch = Switch(
            name=data['name'],
            label=data.get('label'),
            state=data['state'],
            concent=data['concent'],
            compounded=data['conditions']['quantifier'] == 'all'
        )

        for dataconditon in data['conditions']['conditions']:
            condition = Condition(
                argument=self.registry.arguments[dataconditon['argument']],
                attribute=dataconditon['attribute'],
                operator=self.registry.operators[dataconditon['operator']],
                negative=dataconditon['negative'],
            )
            switch.conditions.append(condition)

        return switch
