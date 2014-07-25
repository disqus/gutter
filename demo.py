from kazoo.client import KazooClient

kazoo = KazooClient()
kazoo.start()

kazoo.delete('/hackweek', recursive=True)

from gutter.client.encoding import SwitchProtobufEncoding
from gutter.client.settings import manager as manager_settings
from durabledict.zookeeper import ZookeeperDict

encoding = SwitchProtobufEncoding()
zkstorage = ZookeeperDict(kazoo, '/hackweek', encoding=encoding)
manager_settings.storage_engine = zkstorage
manager_settings.autocreate = True

from gutter.client.default import gutter
from gutter.client.models import (
    Condition,
    Switch,
)
from gutter.client import arguments


class DogeArgument(arguments.Container):
    COMPATIBLE_TYPE = object
    age = arguments.Value(lambda self: 42)
    name = arguments.String(lambda self: "doge")
    ip = "127.0.0.1"

from gutter.client.operators import comparable

OPERATORS = {
    'Equals': comparable.Equals,
    'Between': comparable.Between,
    'MoreThan': comparable.MoreThan,
    'LessThan': comparable.LessThan,
}

PROMPT = """Guess the doge age! Use conditions in the format of:

    $ Operator(arg1[, arg2])

Valid Operators are:

    * Equals(int)
    * Between(int, int)
    * MoreThan(int)
    * LessThan(int)

Type "prompt" again for this prompt.
"""

encoding.registry.arguments.register('doge', DogeArgument)

print PROMPT

switch = Switch('doge', state=Switch.states.DISABLED)
gutter.register(switch)

while True:
    try:
        condition_str = raw_input("$ ")

        if condition_str == "prompt":
            print PROMPT
            continue

        operator_str, argstring = condition_str.split('(')
        raw_args = argstring.strip(')').split(',')

        operator = OPERATORS[operator_str]

        kwargs = {k: int(v) for (k, v) in zip(operator.arguments, raw_args)}

        operator = operator(**kwargs)

        condition = Condition(
            argument=DogeArgument,
            attribute='age',
            operator=operator
        )

        name_parts = [operator.name]
        name_parts.extend(
            map(str, (getattr(operator, arg) for arg in operator.arguments))
        )
        encoding.registry.operators.register(':'.join(name_parts), operator)
        switch.conditions = [condition]
        switch.save()
    except:
        # raise
        print "!! Error processing input please try again"
    else:
        print "Set: " + str(condition)
