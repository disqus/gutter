from modeldict.dict import MemoryDict
from gargoyle.client.operators.comparable import *
from gargoyle.client.operators.identity import *
from gargoyle.client.operators.misc import *


class manager(object):
    storage_engine = MemoryDict()
    autocreate = False
    inputs = []
    operators = (Equals, Between, LessThan, LessThanOrEqualTo, MoreThan,
                 MoreThanOrEqualTo, Truthy, Percent, PercentRange)
