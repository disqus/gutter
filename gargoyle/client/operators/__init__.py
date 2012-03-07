import inspect


class GetInitArguments(object):

        def __get__(self, obj, obj_type):
            print obj_type
            args = inspect.getargspec(obj_type.__init__).args
            return tuple(args[1:])


class Base(object):

    def __init__(self):
        pass

    arguments = GetInitArguments()
