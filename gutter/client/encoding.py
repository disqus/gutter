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
