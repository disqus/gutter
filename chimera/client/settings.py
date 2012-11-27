from modeldict import MemoryDict
from chimera.client.operators.comparable import *
from chimera.client.operators.identity import *
from chimera.client.operators.misc import *


class manager(object):
    storage_engine = MemoryDict()
    autocreate = False
    inputs = []
    operators = (Equals, Between, LessThan, LessThanOrEqualTo, MoreThan,
                 MoreThanOrEqualTo, Truthy, Percent, PercentRange)
    default = None
