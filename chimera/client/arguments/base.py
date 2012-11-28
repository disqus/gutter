class Base(object):
    """
    Base class for Arguments, which are responsible for understanding inputs
    and returning Argument Variables.  Argument variables are compared against
    the Operator inside of a Condition, for deciding if a condition applies to
    the specified input.
    """

    def __init__(self, inpt):
        self.input = inpt

    @property
    def applies(self):
        return False