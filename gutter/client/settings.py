from durabledict import MemoryDict
from gutter.client.encoding import JsonPickleEncoding


class manager(object):
    storage_engine = MemoryDict(encoding=JsonPickleEncoding)
    autocreate = False
    inputs = []
    default = None
