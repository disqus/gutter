class Base(object):

    def __init__(self):
        pass  # Needed to make GetInitArguments work on Base

    @property
    def arguments(self):
        return vars(self)

    def __eq__(self, other):
        for arg in vars(self).keys():
            if getattr(self, arg) != getattr(other, arg):
                return False

        return True

