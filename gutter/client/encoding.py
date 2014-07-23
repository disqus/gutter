from gutter.client.models import (
    Condition,
    Switch,
)
from gutter.client.registry import (
    arguments,
    operators,
)
from gutter.client.interfaces.interfaces_pb2 import (
    Condition as PBCondition,
    Switch as PBSwitch,
)

# XXX: Groos
STATES = vars(Switch.states)

class SwitchProtobufEncoding(object):

    @staticmethod
    def encode(switch):
        pbswitch = PBSwitch()

        pbswitch.name = switch.name

        if switch.label:
            pbswitch.label = switch.label

        pbswitch.concent = switch.concent
        pbswitch.state = switch.state

        # if switch.compounded:
        #     switch.conditions.quantifier = PBConditionList.ALL
        # else:
        #     switch.conditions.quantifier = PBConditionList.ANY

        for condition in switch.conditions:
            pbcondition = PBCondition()
            # pbcondition.argument =
            pbcondition.attribute = condition.attribute
            pbcondition.operator = condition.operator
            pbcondition.negative = condition.negative

            switch.conditions.conditions.add(condition)

        return pbswitch.SerializeToString()

    @staticmethod
    def decode(data):
        pbswitch = PBSwitch()

        pbswitch.ParseFromString(data)

        switch = Switch(
            name=pbswitch.name,
            label=pbswitch.label,
            # XXX: This only works cause the numbers are synced. Should
            #      this change?
            state=pbswitch.state,
            concent=pbswitch.concent,
            compounded=pbswitch.compounded,
        )

        for pbcondition in pbswitch.conditions.conditions:
            condition = Condition(
                argument=arguments[pbcondition.argument],
                attribute=pbcondition.attribute,
                operator=operators[pbcondition.operator],
                negative=pbcondition.negative,
            )
            switch.conditions.append(condition)

        return switch
