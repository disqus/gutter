import inspect


class GetInitArguments(object):

        def __get__(self, obj, obj_type):
            args = inspect.getargspec(obj_type.__init__).args
            return tuple(args[1:])


class Base(object):

    def __init__(self):
        pass  # Needed to make GetInitArguments work on Base

    def __eq__(self, other):
        for arg in vars(self).keys():
            if getattr(self, arg) != getattr(other, arg):
                return False

        return True

    arguments = GetInitArguments()
