from durabledict import MemoryDict


class manager(object):
    storage_engine = MemoryDict()
    autocreate = False
    inputs = []
    default = None
